import os
import sys
import time
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Ensure safe UTF-8 terminal encoding on all systems
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from gemini_editor import analyze_property_with_gemini
from generator import generate_3d_clip
from editor import polish_clip
from telegram_service import TelegramReviewBot
from scraper_service import fetch_fresh_leads

load_dotenv()


def run_pipeline(leads: list, dry_run: bool = False):
    """
    Main orchestration loop with Telegram Human-in-the-Loop Approval:
    1. Gemini Multimodal Analysis: Analyzes scene, builds cinematic prompt & custom copy.
    2. Generates 5s 3D AI video clip (via Replicate Kling AI or local 3D dolly engine).
    3. Polishes clip with dynamic lower-third badge & ambient audio.
    4. Sends Video & Details directly to Telegram for User Approval [Approve / Regenerate / Skip].
    5. On Approval -> Uploads to Drive -> Sends Outreach Email -> Logs to Google Sheets.
    6. On Regenerate -> Gemini re-prompts with alternative angles and re-renders.
    """
    sender_email = os.getenv("GMAIL_SENDER_EMAIL")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")
    google_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "credentials.json")

    has_gmail = (
        bool(sender_email)
        and sender_email != "your_email@gmail.com"
        and bool(sender_password)
    )
    has_drive = os.path.exists(google_creds)

    drive_service = None
    if has_drive:
        try:
            from drive_service import get_drive_service
            drive_service = get_drive_service()
        except Exception as e:
            print(f"[Drive Notice] Google Drive API init warning: {e}")

    telegram_bot = TelegramReviewBot()

    for lead in leads:
        print(f"\n>> Processing lead: {lead['company']} ({lead['property_name']})...")
        approved = False
        attempts = 0
        max_attempts = 3

        while not approved and attempts < max_attempts:
            attempts += 1
            raw_mp4 = f"temp_raw_{lead['id']}.mp4"
            final_mp4 = f"preview_{lead['id']}.mp4"

            try:
                # 1. Gemini Vision Multimodal Inspection & Copy Director
                print(f"  [1/5] 🤖 Gemini Vision Director: Inspecting host listing photo ({lead['company']})...")
                gemini_plan = analyze_property_with_gemini(
                    property_name=lead["property_name"],
                    property_type=lead.get("scene_type", "pool terrace"),
                    image_url=lead.get("photo_url")
                )
                print(f"        -> Visuals Seen: \"{gemini_plan.get('visual_elements_seen', '')[:75]}...\"")
                print(f"        -> Selected 3D Camera: {gemini_plan.get('best_3d_camera_motion', 'dolly_forward')}")
                print(f"        -> Generated Hook: \"{gemini_plan['email_hook']}\"")
                print(f"        -> Dynamic Badge: [{gemini_plan['badge_title']} | {gemini_plan['badge_subtitle']}]")

                # 2. Generate Real AI Clip with Specific Camera Choreography
                print(f"  [2/5] 🎬 Generating 5s 3D video walkthrough ({gemini_plan.get('best_3d_camera_motion')})...")
                generate_3d_clip(
                    image_url=lead["photo_url"],
                    property_type=lead.get("scene_type", "pool terrace"),
                    output_path=raw_mp4,
                    camera_motion=gemini_plan.get("best_3d_camera_motion", "dolly_forward"),
                    prompt=gemini_plan.get("cinematic_prompt")
                )

                # 3. Post-Process Video with Dynamic Badge Overlay
                ambient_audio = "assets/ambient_breeze.mp3"
                print(f"  [3/5] 🎨 Post-processing lower-third overlay & ambient audio...")
                polish_clip(
                    raw_mp4,
                    gemini_plan["badge_title"],
                    ambient_audio,
                    final_mp4,
                    subtitle=gemini_plan["badge_subtitle"]
                )
                print(f"        -> Final video rendered: {final_mp4} ({os.path.getsize(final_mp4) if os.path.exists(final_mp4) else 0} bytes)")

                # 4. Telegram Human-in-the-Loop Review
                print(f"  [4/5] 📱 Telegram Review: Sending video preview directly to your Telegram...")
                telegram_bot.send_video_for_review(
                    lead=lead,
                    gemini_plan=gemini_plan,
                    video_path=final_mp4 if os.path.exists(final_mp4) else None,
                    drive_link=None
                )

                # Wait for user button click on Telegram
                decision = telegram_bot.wait_for_user_decision(lead["id"], timeout_seconds=120)

                if decision == "approve":
                    approved = True
                    print("  [Telegram HITL] ✅ User APPROVED! Proceeding with Drive upload and outreach...")

                    # 5. Upload to Google Drive (if configured)
                    drive_link = f"https://ai-automation-portfolio-seven.vercel.app/#video-showcase"
                    if drive_service and os.path.exists(final_mp4):
                        try:
                            from drive_service import upload_to_drive
                            drive_link = upload_to_drive(
                                drive_service,
                                final_mp4,
                                f"{lead['property_name']}_preview.mp4"
                            )
                            print(f"        -> Public Drive Link: {drive_link}")
                        except Exception as e:
                            print(f"        -> [Drive warning: {e}] Using portfolio link.")

                    # 6. Send Email
                    print(f"  [5/5] ✉️ Dispatching outreach email to {lead['email']}...")
                    if has_gmail and not dry_run:
                        try:
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
                            print(f"        -> Email successfully dispatched via Gmail SMTP to {lead['email']}!")
                            telegram_bot.send_message(f"✉️ <b>Email Sent!</b> Outreach email delivered to <code>{lead['email']}</code>.")
                        except Exception as e:
                            print(f"        -> [Mailer Error] Failed to send email: {e}")
                            telegram_bot.send_message(f"⚠️ <b>Email Failed:</b> {e}")
                    else:
                        print(f"        -> [Notice] Gmail credentials not set. Simulated dispatch to {lead['email']}.")
                        telegram_bot.send_message(
                            f"ℹ️ <b>Approved!</b> Video generated successfully.\n"
                            f"<i>(To send real emails to {lead['email']}, set GMAIL_SENDER_EMAIL & GMAIL_APP_PASSWORD in .env)</i>"
                        )

                    # 7. Log to Google Sheet
                    pitch_date = datetime.now().strftime("%Y-%m-%d")
                    follow_up = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

                    if has_drive and not dry_run:
                        try:
                            from sheets_service import log_lead_to_sheet
                            log_lead_to_sheet(
                                company=lead["company"],
                                email=lead["email"],
                                prop_name=lead["property_name"],
                                drive_link=drive_link,
                                date_pitched=pitch_date,
                                follow_up_due=follow_up
                            )
                            print(f"        -> Appended Row to Google Sheet: [{lead['company']}, {lead['email']}]")
                        except Exception as e:
                            print(f"        -> Sheets log warning: {e}")
                    else:
                        print(f"        -> Appended Row (Local Log): [{lead['company']}, {lead['email']}, {lead['property_name']}, {pitch_date}, 'Pitched']")

                    print(f"[+] Successfully pitched and logged {lead['company']}.\n")

                elif decision == "regen":
                    print("  [Telegram HITL] 🔄 User requested REGENERATION! Retrying with fresh Gemini angle...")
                    time.sleep(1)
                    continue

                elif decision == "skip":
                    print(f"  [Telegram HITL] ❌ Lead {lead['company']} SKIPPED by user. Moving to next lead.\n")
                    break

            except Exception as e:
                print(f"[-] Error processing lead {lead['company']}: {e}")
                break

            finally:
                # Cleanup local temp video files
                for temp_f in [raw_mp4, final_mp4]:
                    if os.path.exists(temp_f):
                        try:
                            os.remove(temp_f)
                        except Exception:
                            pass


if __name__ == "__main__":
    print("\n" + "=" * 65)
    print("🚀 Starting Daily Autonomous Outreach Engine (5 Fresh Leads/Day)...")
    print("=" * 65)

    # 1. Dynamically Scrape / Ingest Fresh Leads
    daily_leads = fetch_fresh_leads(target_count=5, target_location="Marbella, Spain")
    print(f"[*] Ingested {len(daily_leads)} uncontacted luxury real estate listings for today's run.\n")

    # 2. Run Pipeline through Gemini Video Director, Replicate, Drive, Mailer, Sheets
    run_pipeline(daily_leads)

