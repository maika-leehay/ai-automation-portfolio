import os
import sys
import smtplib

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from core.llm import generate_json


def draft_b2b_pitch(business_name: str, business_type: str, city: str, service_offered: str = "AI Video & Workflow Automation") -> dict:
    """
    Generates a personalized high-ticket B2B cold email proposal for local SMBs.
    """
    prompt = f"""
You are an expert enterprise B2B cold email copywriter with a 35% reply rate.
Draft a personalized cold outreach email for:
- Business: {business_name}
- Type: {business_type}
- Location: {city}
- Service: {service_offered}

Return a structured JSON with:
1. "subject_line": 3-4 word curiosity-driven subject (e.g. 'quick question about {business_name}')
2. "opening_hook": Specific compliment on their presence/reputation in {city}
3. "value_proposition": Exactly how {service_offered} will increase their revenue / save 20+ hours weekly
4. "call_to_action": Soft, no-pressure call to action (e.g. 'Open to seeing a 2-minute Loom demo this Thursday?')
5. "full_email_body": The full ready-to-send email body.

JSON:
{{
  "subject_line": "...",
  "opening_hook": "...",
  "value_proposition": "...",
  "call_to_action": "...",
  "full_email_body": "..."
}}
"""
    print(f"\n[Lead Outreach] 🏢 Crafting high-ticket B2B pitch for: '{business_name}'...")
    data = generate_json(prompt)

    if not data or "full_email_body" not in data:
        data = {
            "subject_line": f"Quick question regarding {business_name}",
            "opening_hook": f"I came across {business_name} while researching top {business_type} businesses in {city}.",
            "value_proposition": f"We build automated {service_offered} systems that help businesses capture more qualified clients without manual follow-ups.",
            "call_to_action": "Would you be against seeing a short 2-minute video example of how this works?",
            "full_email_body": f"Hi {business_name} Team,\n\nI came across {business_name} in {city} and was impressed by your work.\n\nWe build custom {service_offered} that automate client acquisition and follow-up.\n\nWould you be open to a quick 2-minute demo of how this could work for your business?\n\nBest,\nMekaoui Abdelmounaim\nAI Automation Architect"
        }

    return data


def send_email_pitch(recipient_email: str, subject: str, body: str) -> bool:
    """
    Dispatches the cold outreach email via SMTP.
    """
    sender_email = os.getenv("GMAIL_SENDER_EMAIL")
    sender_password = os.getenv("GMAIL_APP_PASSWORD")

    if not sender_email or sender_email == "your_email@gmail.com" or not sender_password:
        print(f"  [Outreach Notice] Live SMTP credentials not configured in .env (Simulated send to {recipient_email})")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = recipient_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
        print(f"  [+] Outreach email successfully delivered to {recipient_email}!")
        return True
    except Exception as e:
        print(f"  [-] Failed to send email to {recipient_email}: {e}")
        return False
