import os
import resend
from app.core.config import settings
import base64
from pathlib import Path

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


def send_pdf_email(to_email: str, story_url: str):
    image_url = "https://storage.googleapis.com/koalory_bucket/your_story_is_ready.png"

    params = resend.Emails.SendParams(**{
        "from": "Koalory <noreply@koalory.com>",
        "to": [to_email],
        "subject": "✨ Your personal story is ready! + special offer inside",
        "html": f"""
        <div style="font-family: Arial, sans-serif; font-size: 16px; color: #333; line-height: 1.6; max-width: 600px; margin: auto;">
            <img src="{image_url}" alt="Koalory Banner"
                style="width: 100%; max-width: 600px; height: auto; display: block; margin-bottom: 20px;" />

            <p>Hi there!</p>

            <p>Your personal story is ready! 🎉</p>

            <p style="margin: 20px 0;">
                <a href="{story_url}" style="display: inline-block; background-color: #1a73e8; color: #fff;
                padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    👆 READ YOUR STORY
                </a>
            </p>

            <p>How do you like it? We put all the AI magic into creating <strong>YOUR</strong> unique story with your interests, hobbies, and personality.</p>

            <p style="font-weight: bold;">⏰ NEXT 10 MINUTES ONLY!</p>

            <p>While you're reading your first story, you have a unique opportunity:</p>

            <p>🎁 <strong>3 PERSONAL STORIES for just $5.99</strong> (instead of $8.97)</p>
            <p>Save $2.98 = almost a whole story for free!</p>

            <ul style="padding-left: 20px;">
                <li>✅ 3 unique stories about any characters</li>
                <li>✅ Any genres and moods</li>
                <li>✅ High-quality illustrations</li>
                <li>✅ Email delivery in 5 minutes</li>
            </ul>

            <p style="margin: 20px 0;">
                <a href="https://story.koalory.com/pricing" style="display: inline-block; background-color: #34a853; color: #fff;
                padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                    👉 GET 3 STORIES FOR $5.99
                </a>
            </p>

            <p style="margin-top: 30px;">Offer valid for 10 minutes only after receiving this email</p>

            <p>With love,<br>Koalory Team ✨</p>
        </div>
        """.strip()
    })

    return resend.Emails.send(params)