import sendgrid
import resend
from sendgrid.helpers.mail import Mail
import os

SENDGRID_API_KEY = os.getenv("SENDGRID_API_KEY")

async def send_email_code(to_email: str, code: str):
    r = resend.Emails.send(resend.Emails.SendParams(**{
        "from": "onboarding@resend.dev",
        "to": to_email,
        "subject": "Email Verification Code",
        "html": f"<strong>Your code is: {code}</strong>"}))

async def send_reset_email(to_email: str, token: str):
    url = f"https://story.koalory.com/auth/reset?reset_token={token}"

    r = resend.Emails.send(resend.Emails.SendParams(**{
        "from": "onboarding@resend.dev",
        "to": to_email,
        "subject": "Reset Your Password",
        "html": f"<p>Click <a href=\"{url}\">here</a> to reset your password. This link expires in 1 hour.</p>"}
    ))


