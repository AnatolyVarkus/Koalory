from google.oauth2 import service_account

try:
    creds = service_account.Credentials.from_service_account_file(
        "/home/koalory_bot/Koalory/app/koalory_google.json"
    )
    print("✅ Loaded credentials for:", creds.service_account_email)
except Exception as e:
    print("❌ Failed to load credentials:", e)