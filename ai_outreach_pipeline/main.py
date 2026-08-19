import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Ensure safe UTF-8 terminal encoding on all systems (including Windows cp1252)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()


def run_pipeline(leads: list, dry_run: bool = False):
    """
    Main orchestration loop:
    1. Generates 3D AI video clip via Replicate.
    2. Polishes clip with text banner & ambient sound.
    3. Uploads polished clip to Google Drive with public viewer permissions.
    4. Sends personalized outreach email via Gmail SMTP.
    5. Logs activity and follow-up deadline to Google Sheets.
    """
    sender_email = os.getenv("GMAIL_SENDER_EMAIL", "your_email@gmail.com")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    replicate_token = os.getenv("REPLICATE_API_TOKEN")
    google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

    has_live_credentials = (
        bool(replicate_token)
        and os.path.exists(google_creds)
        and bool(sender_password)
    )

    is_dry_run = dry_run or not has_live_credentials

    if is_dry_run:
        print("=" * 65)
        print(" [DRY RUN / SIMULATION MODE ACTIVATED]")
        print(" Live API keys / credentials.json not configured in .env.")
        print(" Demonstrating full workflow execution, pipeline flow & data output.")
        print("=" * 65)

    drive_service = None
    if not is_dry_run:
        from drive_service import get_drive_service
        drive_service = get_drive_service()

    for lead in leads:
        print(f"\n>> Processing lead: {lead['company']} ({lead['property_name']})...")

        try:
            # 1. Generate Raw AI Clip
            raw_mp4 = f"temp_raw_{lead['id']}.mp4"
            print("  [1/5] Generating 5s 3D cinematic video clip...")
            if not is_dry_run:
                from generator import generate_3d_clip
                generate_3d_clip(lead["photo_url"], lead.get("scene_type", "pool terrace"), raw_mp4)
            else:
                time.sleep(0.6)
                print(f"        -> Prompt dispatched to Replicate (kling-ai/kling-v1.5) for {lead['photo_url']}")
                print(f"        -> Rendered 5-second video downloaded to: {raw_mp4}")

            # 2. Post-Process Video
            final_mp4 = f"preview_{lead['id']}.mp4"
            ambient_audio = "assets/ambient_breeze.mp3"
            print(f"  [2/5] Post-processing lower-third overlay '{lead['property_name'].upper()}' & ambient audio...")
            if not is_dry_run:
                from editor import polish_clip
                polish_clip(raw_mp4, lead["property_name"], ambient_audio, final_mp4)
            else:
                time.sleep(0.5)
                print(f"        -> Video rendered: {final_mp4} (30 fps, H.264 / AAC)")

            # 3. Upload to Google Drive
            print("  [3/5] Uploading to Google Drive and setting public viewer link...")
            if not is_dry_run:
                from drive_service import upload_to_drive
                drive_link = upload_to_drive(
                    drive_service,
                    final_mp4,
                    f"{lead['property_name']}_preview.mp4"
                )
            else:
                time.sleep(0.4)
                drive_link = f"https://drive.google.com/file/d/demo_{lead['id']}_xyz123/view?usp=sharing"
            print(f"        -> Public Drive Link: {drive_link}")

            # 4. Send Email
            print(f"  [4/5] Sending personalized outreach email to {lead['email']}...")
            if not is_dry_run:
                from mailer import send_outreach_email
                send_outreach_email(
                    sender_email=sender_email,
                    sender_password=sender_password,
                    recipient_email=lead["email"],
                    company=lead["company"],
                    prop_name=lead["property_name"],
                    drive_link=drive_link
                )
            else:
                time.sleep(0.4)
                print(f"        -> Email dispatched via SMTP with customized copy to {lead['email']}")

            # 5. Log to Google Sheet
            print("  [5/5] Logging lead to Google Sheets tracking spreadsheet...")
            pitch_date = datetime.now().strftime("%Y-%m-%d")
            follow_up = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

            if not is_dry_run:
                from sheets_service import log_lead_to_sheet
                log_lead_to_sheet(
                    company=lead["company"],
                    email=lead["email"],
                    prop_name=lead["property_name"],
                    drive_link=drive_link,
                    date_pitched=pitch_date,
                    follow_up_due=follow_up
                )
            else:
                time.sleep(0.3)
                print(f"        -> Appended Row: [{lead['company']}, {lead['email']}, {lead['property_name']}, {drive_link}, {pitch_date}, {follow_up}, 'Pitched']")

            # Cleanup local temp files if they exist
            for temp_f in [raw_mp4, final_mp4]:
                if os.path.exists(temp_f):
                    try:
                        os.remove(temp_f)
                    except Exception:
                        pass

            print(f"[+] Successfully processed and logged {lead['company']}.\n")

        except Exception as e:
            print(f"[-] Error processing lead {lead['company']}: {e}")


if __name__ == "__main__":
    sample_leads = [
        {
            "id": "lead_001",
            "company": "Azure Horizon Villas",
            "property_name": "Villa Seraphina",
            "scene_type": "pool terrace and infinity ocean view",
            "photo_url": "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?auto=format&fit=crop&w=1200&q=80",
            "email": "contact@azurehorizonvillas.com",
        },
        {
            "id": "lead_002",
            "company": "Emerald Crest Luxury Rentals",
            "property_name": "Penthouse Celeste",
            "scene_type": "modern panoramic skyline balcony",
            "photo_url": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?auto=format&fit=crop&w=1200&q=80",
            "email": "partnerships@emeraldcrest.com",
        }
    ]

    print("\nStarting AI Video Outreach Pipeline Execution...\n")
    run_pipeline(sample_leads)
