import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def send_outreach_email(
    sender_email: str,
    sender_password: str,
    recipient_email: str,
    company: str,
    prop_name: str,
    drive_link: str,
    sender_name: str = "Abdelmounaim Mekaoui",
    custom_hook: str = None,
    selling_points: list = None
):
    """
    Formats the personalized outreach message and sends it via Gmail SMTP.
    """
    hook = custom_hook or f"I came across your listing for {prop_name} and was impressed by the property."
    bullet_points = ""
    if selling_points:
        bullet_points = "\n" + "\n".join([f"  • {pt}" for pt in selling_points]) + "\n"

    subject = f"Quick 3D video preview for {prop_name}"
    body = f"""Hi {company} Team,

{hook}

To demonstrate how dynamic 3D video walkthroughs can help showcase your properties on social media and direct booking channels without on-site filming, I prepared a short 5-second 3D preview:

{drive_link}
{bullet_points}
I produce full 20–30s social-ready walkthrough reels (with ambient audio, amenity callouts, and smooth camera motion) with a 24–48h turnaround.

You can explore our interactive 3D video engine and full enterprise automation capabilities on our live portfolio:
https://ai-automation-portfolio-seven.vercel.app/

If you would like to test a full video for one of your featured properties or discuss a monthly video package (€250–€500/mo), I'd be glad to prepare one for you.

Best regards,
{sender_name}
AI Automation & Media Architect
Portfolio: https://ai-automation-portfolio-seven.vercel.app/
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)
