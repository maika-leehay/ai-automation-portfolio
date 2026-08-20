import os
import time
import requests
from dotenv import load_dotenv

load_dotenv()


class TelegramReviewBot:
    def __init__(self, bot_token: str = None, chat_id: str = None):
        self.bot_token = bot_token or os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = chat_id or os.getenv("TELEGRAM_CHAT_ID")
        self.api_url = f"https://api.telegram.org/bot{self.bot_token}"

    def send_message(self, text: str) -> dict:
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        res = requests.post(url, json=payload, timeout=15)
        return res.json()

    def send_video_for_review(
        self,
        lead: dict,
        gemini_plan: dict,
        video_path: str = None,
        drive_link: str = None
    ) -> int:
        """
        Sends the generated 3D video (or photo & drive link) to Telegram with
        interactive inline buttons: [Approve & Send], [Regenerate], [Skip].
        Returns message_id.
        """
        camera_name = gemini_plan.get('best_3d_camera_motion', 'dolly_forward').replace('_', ' ').title()
        visual_desc = gemini_plan.get('visual_elements_seen', '')
        
        caption = (
            f"🎬 <b>AI 3D Video Review Required</b>\n\n"
            f"🏢 <b>Company:</b> {lead['company']}\n"
            f"🏡 <b>Property:</b> {lead['property_name']}\n"
            f"📧 <b>Recipient:</b> {lead['email']}\n"
            f"🎥 <b>3D Motion:</b> <code>{camera_name}</code>\n"
            f"🏷 <b>Badge:</b> <code>{gemini_plan['badge_title']}</code>\n"
            f"✨ <b>Subtitle:</b> {gemini_plan['badge_subtitle']}\n\n"
            f"👁 <b>Visuals Detected:</b>\n<i>\"{visual_desc[:140]}...\"</i>\n\n"
            f"💡 <b>Gemini Hook:</b>\n<i>\"{gemini_plan['email_hook']}\"</i>\n"
        )
        if drive_link:
            caption += f"\n🔗 <a href='{drive_link}'>View Video Link</a>"

        reply_markup = {
            "inline_keyboard": [
                [
                    {"text": "✅ Approve & Send Email", "callback_data": f"approve_{lead['id']}"}
                ],
                [
                    {"text": "🔄 Regenerate Video", "callback_data": f"regen_{lead['id']}"},
                    {"text": "❌ Skip Lead", "callback_data": f"skip_{lead['id']}"}
                ]
            ]
        }

        # If a real local MP4 exists, send as native video
        if video_path and os.path.exists(video_path):
            try:
                url = f"{self.api_url}/sendVideo"
                with open(video_path, "rb") as video_file:
                    files = {"video": video_file}
                    data = {
                        "chat_id": self.chat_id,
                        "caption": caption,
                        "parse_mode": "HTML",
                        "reply_markup": requests.compat.json.dumps(reply_markup)
                    }
                    res = requests.post(url, data=data, files=files, timeout=45)
                    res_json = res.json()
                    if res_json.get("ok"):
                        return res_json["result"]["message_id"]
            except Exception as e:
                print(f"[Telegram] Failed to send video file ({e}), falling back to photo/text.")

        # If photo_url exists locally or web
        photo = lead.get("photo_url")
        if photo and os.path.exists(photo):
            url = f"{self.api_url}/sendPhoto"
            with open(photo, "rb") as pf:
                files = {"photo": pf}
                data = {
                    "chat_id": self.chat_id,
                    "caption": caption,
                    "parse_mode": "HTML",
                    "reply_markup": requests.compat.json.dumps(reply_markup)
                }
                res = requests.post(url, data=data, files=files, timeout=30)
                res_json = res.json()
                if res_json.get("ok"):
                    return res_json["result"]["message_id"]

        # Default text message with buttons
        url = f"{self.api_url}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": caption,
            "parse_mode": "HTML",
            "reply_markup": reply_markup
        }
        res = requests.post(url, json=payload, timeout=15)
        res_json = res.json()
        return res_json.get("result", {}).get("message_id", 0)

    def wait_for_user_decision(self, lead_id: str, timeout_seconds: int = 300) -> str:
        """
        Polls Telegram updates for user button click on the inline keyboard.
        Returns: 'approve', 'regen', or 'skip'.
        """
        print(f"  [Telegram HITL] ⏳ Waiting for your approval on Telegram for lead: {lead_id}...")
        start_time = time.time()
        last_update_id = 0

        # Flush prior updates
        try:
            flush_res = requests.get(f"{self.api_url}/getUpdates?offset=-1", timeout=10).json()
            if flush_res.get("result"):
                last_update_id = flush_res["result"][-1]["update_id"]
        except Exception:
            pass

        while time.time() - start_time < timeout_seconds:
            try:
                url = f"{self.api_url}/getUpdates?offset={last_update_id + 1}&timeout=5"
                res = requests.get(url, timeout=10).json()
                if res.get("ok") and res.get("result"):
                    for update in res["result"]:
                        last_update_id = update["update_id"]
                        callback = update.get("callback_query")
                        if callback:
                            data = callback.get("data", "")
                            cb_id = callback.get("id")

                            # Answer callback query to stop loading spinner on user screen
                            requests.post(f"{self.api_url}/answerCallbackQuery", json={"callback_query_id": cb_id})

                            if data == f"approve_{lead_id}":
                                requests.post(f"{self.api_url}/sendMessage", json={
                                    "chat_id": self.chat_id,
                                    "text": f"✅ <b>Approved!</b> Dispatching email & logging sheet now...",
                                    "parse_mode": "HTML"
                                })
                                return "approve"

                            elif data == f"regen_{lead_id}":
                                requests.post(f"{self.api_url}/sendMessage", json={
                                    "chat_id": self.chat_id,
                                    "text": f"🔄 <b>Regenerating!</b> Gemini is crafting a new angle and video prompt...",
                                    "parse_mode": "HTML"
                                })
                                return "regen"

                            elif data == f"skip_{lead_id}":
                                requests.post(f"{self.api_url}/sendMessage", json={
                                    "chat_id": self.chat_id,
                                    "text": f"❌ <b>Skipped!</b> Lead discarded with no emails sent.",
                                    "parse_mode": "HTML"
                                })
                                return "skip"

            except Exception as e:
                time.sleep(1)

            time.sleep(1.5)

        print("  [Telegram HITL] ⚠️ Review timeout exceeded (5 mins). Auto-skipping lead.")
        return "skip"
