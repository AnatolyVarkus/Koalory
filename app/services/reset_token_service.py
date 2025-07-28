from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
import os

SECRET_KEY = os.getenv("RESET_SECRET_KEY", "super-secret-key")
serializer = URLSafeTimedSerializer(SECRET_KEY)

def generate_reset_token(email: str) -> str:
    return serializer.dumps(email, salt="reset-salt-2003")

def verify_reset_token(token: str, max_age_sec: int = 3600) -> str:
    try:
        email = serializer.loads(token, salt="reset-salt-2003", max_age=max_age_sec)
        return email
    except SignatureExpired:
        raise ValueError("Token expired")
    except BadSignature:
        raise ValueError("Invalid token")