import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import os

load_dotenv()


EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASS = os.getenv("EMAIL_PASS")
TO_EMAIL = EMAIL_USER

msg = MIMEMultipart()
msg["From"] = EMAIL_USER
msg["To"] = TO_EMAIL
msg["Subject"] = "Test Email"
body = "This is a test email sent using Gmail SMTP."
msg.attach(MIMEText(body, "plain"))

with smtplib.SMTP("smtp.gmail.com", 587) as server:
    server.starttls()
    server.login(EMAIL_USER, EMAIL_PASS)
    server.sendmail(EMAIL_USER, TO_EMAIL, msg.as_string())

print("Email sent successfully!")
