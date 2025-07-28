import sendgrid
import resend
from sendgrid.helpers.mail import Mail
import os
from app.core.config import settings

resend.api_key = settings.RESEND_API_KEY

#
def send_email_code(to_email: str, code: str):
    print(f"Code: {code}")
    r = resend.Emails.send(resend.Emails.SendParams(**{
        "from": "Koalory <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "Email Verification Code",
        "html": f"<strong>Your code is: {code}</strong>"}))

def send_reset_email(to_email: str, token: str):
    url = f"https://story.koalory.com/auth/reset?reset_token={token}"
    print(f"Token: {token}")
    print(f"URL: {url}")

    params = resend.Emails.SendParams(**{
        "from": "Koalory <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "Reset Your Password",
        "html": f"<p>Click <a href=\"{url}\">here</a> to reset your password. This link expires in 1 hour.</p>"})
    r = resend.Emails.send(params)

def send_pdf_email(to_email: str, url: str):

    params = resend.Emails.SendParams(**{
        "from": "Koalory <onboarding@resend.dev>",
        "to": [to_email],
        "subject": "Reset Your Password",
        "html": f"""
    <div style="font-family: Arial, sans-serif; font-size: 16px; color: #333;">
        <p>Your story is ready!</p>
        <p>
            You can check it out here:
            <a href="{url}" style="color: #1a73e8; text-decoration: none;">
                <strong>Click to view your story</strong>
            </a>
        </p>
        <p style="margin-top: 20px;">Enjoy!</p>
    </div>
""".strip()})
    r = resend.Emails.send(params)