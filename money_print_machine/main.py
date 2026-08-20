import os
import sys
import time
from dotenv import load_dotenv

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

load_dotenv()

from modules.shorts_generator import generate_short
from modules.twitter_monetizer import generate_viral_thread
from modules.affiliate_automator import generate_affiliate_campaign
from modules.lead_outreach import draft_b2b_pitch, send_email_pitch
from telegram_bot import TelegramMoneyBot


def print_banner():
    banner = """
======================================================================
  💰 MONEY PRINT MACHINE - Autonomous Multi-Engine Revenue Stack 💰
======================================================================
  [1] 🎬 Generate YouTube Short / TikTok (AI Script + Voice + Subtitles)
  [2] 🐦 Generate Viral Twitter / X Thread (High Retention & CTA)
  [3] 💰 Generate Affiliate Product Campaign (Review & Social Copy)
  [4] 🏢 Generate Local B2B Client Audit & Cold Outreach Pitch
  [5] 🤖 Launch Telegram Remote Controller (Control via @MekaouiBot)
  [6] ⏰ Run Autonomous Autopilot Mode (Scheduled Daily Content)
  [0] 🚪 Exit
======================================================================
"""
    print(banner)


def main():
    telegram = TelegramMoneyBot()

    while True:
        print_banner()
        choice = input("Enter choice [0-6]: ").strip()

        if choice == "1":
            print("\n🎬 Select Niche for YouTube Short / TikTok:")
            print("  1. Wealth & Money Psychology")
            print("  2. Stoic Wisdom for High Performers")
            print("  3. AI Tools That Feel Illegal to Know")
            print("  4. Custom Topic")
            n_choice = input("Choice [1-4]: ").strip()
            
            niche_map = {
                "1": "Wealth Psychology & Money Habits",
                "2": "Stoic Philosophy for High Performers",
                "3": "Mind-Blowing AI Tools That Feel Illegal to Know"
            }
            niche = niche_map.get(n_choice, "Wealth Psychology & Money Habits")
            if n_choice == "4":
                niche = input("Enter custom topic/niche: ").strip() or "Tech & Future Trends"

            res = generate_short(niche=niche)
            print(f"\n[+] Success! Video generated at: {res['video_path']}")
            
            # Send to Telegram
            print("  [Telegram] 📱 Sending generated Short to your Telegram bot...")
            caption = f"🔥 <b>{res['title']}</b>\n\n📝 <i>\"{res['script'][:120]}...\"</i>\n\n🏷 {' '.join(res['tags'])}"
            telegram.send_video(res["video_path"], caption)

        elif choice == "2":
            topic = input("\nEnter niche for Twitter Thread (e.g. AI Automations, SaaS, Real Estate): ").strip() or "AI Automations"
            data = generate_viral_thread(niche=topic)
            print(f"\n🧵 Viral Thread Generated:\n")
            for idx, tweet in enumerate(data.get("thread", [])):
                print(f"--- Tweet {idx+1} ---")
                print(tweet)
                print()

        elif choice == "3":
            prod = input("\nEnter Product Name (e.g. Notion AI, Standing Desk, SaaS CRM): ").strip() or "AI Automation Suite"
            cat = input("Enter Category (e.g. Productivity, Tech, Fitness): ").strip() or "Tech & Productivity"
            data = generate_affiliate_campaign(prod, cat)
            print(f"\n💰 Affiliate Campaign Generated:\n")
            print(f"Headline: {data.get('headline')}\n")
            print(f"Social Post:\n{data.get('social_post')}\n")
            print(f"Email Blast:\n{data.get('email_blast')}\n")

        elif choice == "4":
            biz = input("\nEnter Business Name (e.g. Apex Dental Care, Luxury Living Marbella): ").strip() or "Apex Real Estate"
            btype = input("Enter Business Type (e.g. Real Estate Agency, Dental Clinic): ").strip() or "Real Estate Brokerage"
            city = input("Enter City (e.g. Marbella, Dubai, London): ").strip() or "London"
            pitch = draft_b2b_pitch(biz, btype, city)
            print(f"\n🏢 B2B Proposal Drafted:\n")
            print(f"Subject: {pitch.get('subject_line')}\n")
            print(f"Body:\n{pitch.get('full_email_body')}\n")

        elif choice == "5":
            telegram.poll_commands()

        elif choice == "6":
            print("\n⏰ Autonomous Autopilot Mode Started! (Press Ctrl+C to stop)")
            print("   Scheduled: Daily YouTube Short + Daily Twitter Growth Thread.")
            generate_short()
            generate_viral_thread()

        elif choice == "0":
            print("\nExiting Money Print Machine. Goodbye!\n")
            break


if __name__ == "__main__":
    main()
