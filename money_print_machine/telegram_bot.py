import os
import time
import requests
from dotenv import load_dotenv
from modules.shorts_generator import generate_short
from modules.twitter_monetizer import generate_viral_thread
from modules.affiliate_automator import generate_affiliate_campaign
from modules.lead_outreach import draft_b2b_pitch

load_dotenv()


class TelegramMoneyBot:
    def __init__(self):
        self.bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, text: str) -> bool:
        if not self.bot_token or not self.chat_id:
            return False
        try:
            url = f"{self.api_url}/sendMessage"
            payload = {"chat_id": self.chat_id, "text": text, "parse_mode": "HTML"}
            res = requests.post(url, json=payload, timeout=15)
            return res.json().get("ok", False)
        except Exception as e:
            print(f"[Telegram Send Error] {e}")
            return False

    def send_video(self, video_path: str, caption: str) -> bool:
        if not self.bot_token or not self.chat_id or not os.path.exists(video_path):
            return False
        try:
            url = f"{self.api_url}/sendVideo"
            with open(video_path, "rb") as vf:
                files = {"video": vf}
                data = {"chat_id": self.chat_id, "caption": caption, "parse_mode": "HTML"}
                res = requests.post(url, data=data, files=files, timeout=60)
                return res.json().get("ok", False)
        except Exception as e:
            print(f"[Telegram Video Error] {e}")
            return False

    def poll_commands(self):
        """
        Polls for commands sent from your phone in Telegram.
        """
        print("\n" + "=" * 60)
        print("🤖 Telegram Controller Bot Active! Waiting for phone commands...")
        print("   Commands you can send from Telegram:")
        print("   • /short    - Generates and delivers a vertical 9:16 Short")
        print("   • /thread   - Generates a 5-part viral Twitter thread")
        print("   • /pitch    - Generates a high-ticket B2B outreach pitch")
        print("   • /help     - Displays command list")
        print("=" * 60 + "\n")

        self.send_message(
            "🚀 <b>Money Print Machine Online!</b>\n\n"
            "Send any command:\n"
            "👉 <code>/short</code> - Generate a viral YouTube Short / TikTok video\n"
            "👉 <code>/thread</code> - Generate a viral Twitter thread\n"
            "👉 <code>/pitch</code> - Generate a high-ticket B2B outreach pitch"
        )

        last_update_id = 0
        while True:
            try:
                url = f"{self.api_url}/getUpdates?offset={last_update_id + 1}&timeout=10"
                res = requests.get(url, timeout=15).json()
                if res.get("ok") and res.get("result"):
                    for update in res["result"]:
                        last_update_id = update["update_id"]
                        msg = update.get("message", {})
                        text = msg.get("text", "").strip()

                        if text == "/short" or text.startswith("/short"):
                            self.send_message("🎬 <b>Generating YouTube Short / TikTok...</b>\n<i>Writing script, synthesizing voice & rendering video...</i>")
                            short_data = generate_short()
                            caption = (
                                f"🔥 <b>{short_data['title']}</b>\n\n"
                                f"📝 <i>\"{short_data['script'][:120]}...\"</i>\n\n"
                                f"🏷 {' '.join(short_data['tags'])}"
                            )
                            self.send_video(short_data["video_path"], caption)

                        elif text == "/thread" or text.startswith("/thread"):
                            self.send_message("🐦 <b>Crafting viral Twitter thread...</b>")
                            thread_data = generate_viral_thread()
                            formatted = f"🧵 <b>Viral Thread: {thread_data['topic']}</b>\n\n"
                            for idx, t in enumerate(thread_data["thread"]):
                                formatted += f"<b>Tweet {idx+1}:</b>\n{t}\n\n"
                            self.send_message(formatted)

                        elif text == "/pitch" or text.startswith("/pitch"):
                            self.send_message("🏢 <b>Drafting B2B outreach proposal...</b>")
                            pitch_data = draft_b2b_pitch("Summit Real Estate Group", "Luxury Brokerage", "London")
                            self.send_message(
                                f"✉️ <b>B2B Proposal:</b> <code>{pitch_data['subject_line']}</code>\n\n"
                                f"{pitch_data['full_email_body']}"
                            )

            except Exception as e:
                time.sleep(2)

            time.sleep(2)


if __name__ == "__main__":
    bot = TelegramMoneyBot()
    bot.poll_commands()
