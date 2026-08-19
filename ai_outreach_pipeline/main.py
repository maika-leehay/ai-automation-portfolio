import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Ensure safe UTF-8 terminal encoding on all systems (including Windows cp1252)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from gemini_editor import analyze_property_with_gemini

load_dotenv()


def run_pipeline(leads: list, dry_run: bool = False):
    """
    Main orchestration loop:
    1. Gemini Multimodal Analysis: Analyzes scene, builds cinematic prompt & custom copy.
    2. Generates 3D AI video clip via Replicate.
    3. Polishes clip with Gemini text badge & ambient sound.
    4. Uploads polished clip to Google Drive with public viewer permissions.
    5. Sends hyper-personalized outreach email via Gmail SMTP.
    6. Logs activity and follow-up deadline to Google Sheets.
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
        print(" Demonstrating Gemini Video Director + Full Pipeline execution.")
        print("=" * 65)

    drive_service = None
    if not is_dry_run:
        from drive_service import get_drive_service
        drive_service = get_drive_service()

    for lead in leads:
        print(f"\n>> Processing lead: {lead['company']} ({lead['property_name']})...")

        try:
            # 0. Gemini Video Director & Copy Analysis
            print("  [1/6] 🤖 Gemini Director: Analyzing property photo & generating copy...")
            gemini_plan = analyze_property_with_gemini(
                property_name=lead["property_name"],
                property_type=lead.get("scene_type", "pool terrace"),
                image_url=lead.get("photo_url")
            )
            print(f"        -> Generated Hook: \"{gemini_plan['email_hook']}\"")
            print(f"        -> Dynamic Badge: [{gemini_plan['badge_title']} | {gemini_plan['badge_subtitle']}]")

            # 1. Generate Raw AI Clip
            raw_mp4 = f"temp_raw_{lead['id']}.mp4"
            print("  [2/6] 🎬 Generating 5s 3D cinematic video clip...")
            if not is_dry_run:
                from generator import generate_3d_clip
                generate_3d_clip(lead["photo_url"], lead.get("scene_type", "pool terrace"), raw_mp4)
            else:
                time.sleep(0.5)
                print(f"        -> Prompt dispatched: {gemini_plan['cinematic_prompt'][:65]}...")
                print(f"        -> Rendered 5-second video downloaded to: {raw_mp4}")

            # 2. Post-Process Video
            final_mp4 = f"preview_{lead['id']}.mp4"
            ambient_audio = "assets/ambient_breeze.mp3"
            print(f"  [3/6] 🎨 Post-processing Gemini lower-third overlay & ambient audio...")
            if not is_dry_run:
                from editor import polish_clip
                polish_clip(
                    raw_mp4,
                    gemini_plan["badge_title"],
                    ambient_audio,
                    final_mp4,
                    subtitle=gemini_plan["badge_subtitle"]
                )
            else:
                time.sleep(0.4)
                print(f"        -> Video rendered: {final_mp4} (30 fps, H.264 / AAC)")

            # 3. Upload to Google Drive
            print("  [4/6] ☁️ Uploading to Google Drive and setting public viewer link...")
            if not is_dry_run:
                from drive_service import upload_to_drive
                drive_link = upload_to_drive(
                    drive_service,
                    final_mp4,
                    f"{lead['property_name']}_preview.mp4"
                )
            else:
                time.sleep(0.3)
                drive_link = f"https://drive.google.com/file/d/demo_{lead['id']}_xyz123/view?usp=sharing"
            print(f"        -> Public Drive Link: {drive_link}")

            # 4. Send Email
            print(f"  [5/6] ✉️ Sending personalized outreach email to {lead['email']}...")
            if not is_dry_run:
                from mailer import send_outreach_email
                send_outreach_email(
                    sender_email=sender_email,
                    sender_password=sender_password,
                    recipient_email=lead["email"],
                    company=lead["company"],
                    prop_name=lead["property_name"],
                    drive_link=drive_link,
                    custom_hook=gemini_plan["email_hook"],
                    selling_points=gemini_plan["selling_points"]
                )
            else:
                time.sleep(0.3)
                print(f"        -> Email dispatched via SMTP with customized Gemini copy to {lead['email']}")

            # 5. Log to Google Sheet
            print("  [6/6] 📊 Logging lead to Google Sheets tracking spreadsheet...")
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
                time.sleep(0.2)
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
