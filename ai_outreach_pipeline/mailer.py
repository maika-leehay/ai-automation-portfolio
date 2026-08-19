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
    sender_name: str = "Abdelmounaim Mekaoui"
):
    """
    Formats the personalized outreach message and sends it via Gmail SMTP.
    """
    subject = f"Quick 3D video preview for {prop_name}"
    body = f"""Hi {company} Team,

I came across your listing for {prop_name} and was impressed by the property.

To demonstrate how dynamic 3D video walkthroughs can help showcase your properties on social media and direct booking channels without on-site filming, I prepared a short 5-second 3D preview:

{drive_link}

I produce full 20–30s social-ready walkthrough reels (with ambient audio, amenity callouts, and smooth camera motion) with a 24–48h turnaround.

If you would like to test a full video for one of your featured properties, I'd be glad to prepare one for you.

Best regards,
{sender_name}
"""

    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = recipient_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, sender_password)
        server.send_message(msg)
