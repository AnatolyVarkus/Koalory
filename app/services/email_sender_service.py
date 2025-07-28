import os
import resend
from app.core.config import settings

# Set Resend API key
resend.api_key = settings.RESEND_API_KEY


def send_email_code(to_email: str, code: str):
    """
    Sends a verification code to the user's email.
    """
    print(f"[DEBUG] Verification code: {code}")

    params = resend.Emails.SendParams(**{
        "from": "Koalory <noreply@koalory.com>",
        "to": [to_email],
        "subject": "Email Verification Code",
        "html": f"""
            <div style="font-family: Arial, sans-serif; font-size: 16px; color: #333;">
                <p><strong>Your verification code is:</strong> {code}</p>
            </div>
        """.strip()
    })

    return resend.Emails.send(params)


def send_reset_email(to_email: str, token: str):
    """
    Sends a password reset email with a secure link.
    """
    url = f"https://story.koalory.com/auth/reset?reset_token={token}"
    print(f"[DEBUG] Reset token: {token}")
    print(f"[DEBUG] Reset URL: {url}")

    params = resend.Emails.SendParams(**{
        "from": "Koalory <noreply@koalory.com>",
        "to": [to_email],
        "subject": "Reset Your Password",
        "html": f"""
            <div style="font-family: Arial, sans-serif; font-size: 16px; color: #333;">
                <p>Click the link below to reset your password:</p>
                <p>
                    <a href="{url}" style="color: #1a73e8; text-decoration: none;">
                        <strong>Reset Password</strong>
                    </a>
                </p>
                <p>This link will expire in 1 hour.</p>
            </div>
        """.strip()
    })

    return resend.Emails.send(params)


def send_pdf_email(to_email: str, url: str):
    """
    Sends an email with a link to the generated story PDF.
    """
    print(f"[DEBUG] Story URL: {url}")

    params = resend.Emails.SendParams(**{
        "from": "Koalory <noreply@koalory.com>",
        "to": [to_email],
        "subject": "Your Story is Ready!",
        "html": f"""
            <div style="font-family: Arial, sans-serif; font-size: 16px; color: #333;">
                <p>Your story is ready!</p>
                <p>
                    <a href="{url}" style="color: #1a73e8; text-decoration: none;">
                        <strong>Click here to view your story</strong>
                    </a>
                </p>
                <p style="margin-top: 20px;">Enjoy the adventure!</p>
            </div>
        """.strip()
    })

    return resend.Emails.send(params)