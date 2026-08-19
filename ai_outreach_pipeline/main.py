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
from telegram_service import TelegramReviewBot

load_dotenv()


def run_pipeline(leads: list, dry_run: bool = False):
    """
    Main orchestration loop with Telegram Human-in-the-Loop Approval:
    1. Gemini Multimodal Analysis: Analyzes scene, builds cinematic prompt & custom copy.
    2. Generates 3D AI video clip via Replicate.
    3. Polishes clip with Gemini text badge & ambient sound.
    4. Sends Video & Details to Telegram for User Approval [Approve / Regenerate / Skip].
    5. On Approval -> Uploads to Drive -> Sends Outreach Email -> Logs to Google Sheets.
    6. On Regenerate -> Gemini re-prompts with alternative angles and re-renders.
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
        print(" Demonstrating Gemini Video Director + Telegram HITL Approval.")
        print("=" * 65)

    drive_service = None
    if not is_dry_run:
        from drive_service import get_drive_service
        drive_service = get_drive_service()

    telegram_bot = TelegramReviewBot()

    for lead in leads:
        print(f"\n>> Processing lead: {lead['company']} ({lead['property_name']})...")
        approved = False
        attempts = 0
        max_attempts = 3

        while not approved and attempts < max_attempts:
            attempts += 1
            try:
                # 0. Gemini Video Director & Copy Analysis
                print(f"  [1/6] 🤖 Gemini Director: Analyzing property photo & generating copy (Attempt {attempts})...")
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
                    time.sleep(0.4)
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
                    time.sleep(0.3)
                    print(f"        -> Video rendered: {final_mp4} (30 fps, H.264 / AAC)")

                # 3. Telegram Human-in-the-Loop Review
                print(f"  [4/6] 📱 Telegram Review: Sending video preview to your Telegram bot...")
                demo_link = f"https://ai-automation-portfolio-seven.vercel.app/#video-showcase"
                telegram_bot.send_video_for_review(
                    lead=lead,
                    gemini_plan=gemini_plan,
                    video_path=final_mp4 if os.path.exists(final_mp4) else None,
                    drive_link=demo_link
                )

                # Wait for user button click on Telegram
                decision = telegram_bot.wait_for_user_decision(lead["id"], timeout_seconds=120)

                if decision == "approve":
                    approved = True
                    print("  [Telegram HITL] ✅ User APPROVED! Proceeding with Drive upload and outreach...")

                    # 4. Upload to Google Drive
                    print("  [5/6] ☁️ Uploading to Google Drive and setting public viewer link...")
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

                    # 5. Send Email
                    print(f"  [6/6] ✉️ Sending personalized outreach email to {lead['email']}...")
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

                    # 6. Log to Google Sheet
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

                    print(f"[+] Successfully pitched and logged {lead['company']}.\n")

                elif decision == "regen":
                    print("  [Telegram HITL] 🔄 User requested REGENERATION! Retrying with fresh Gemini angle...")
                    time.sleep(1)
                    continue

                elif decision == "skip":
                    print(f"  [Telegram HITL] ❌ Lead {lead['company']} SKIPPED by user. Moving to next lead.\n")
                    break

                # Cleanup local temp files if they exist
                for temp_f in [raw_mp4, final_mp4]:
                    if os.path.exists(temp_f):
                        try:
                            os.remove(temp_f)
                        except Exception:
                            pass

            except Exception as e:
                print(f"[-] Error processing lead {lead['company']}: {e}")
                break


from scraper_service import fetch_fresh_leads

if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("🚀 Starting Daily Autonomous Outreach Engine (5 Fresh Leads/Day)...")
    print("=" * 65)

    # 1. Dynamically Scrape / Ingest Fresh Leads
    daily_leads = fetch_fresh_leads(target_count=5, target_location="Marbella, Spain")
    print(f"[*] Ingested {len(daily_leads)} uncontacted luxury real estate listings for today's run.\n")

    # 2. Run Pipeline through Gemini Video Director, Replicate, Drive, Mailer, Sheets
    run_pipeline(daily_leads)
