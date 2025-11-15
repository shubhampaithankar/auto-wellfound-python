import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Wellfound login credentials
email = os.getenv("WELLFOUND_EMAIL", "")
password = os.getenv("WELLFOUND_PASSWORD", "")

# Email service configuration
# Use Resend (FREE - 3,000 emails/month) - Recommended
# Get API key from: https://resend.com/api-keys
resend_api_key = os.getenv("RESEND_API_KEY", "")

# Email addresses
from_email = os.getenv("FROM_EMAIL", "")  # Email address to send from (can be different from login email)
to_email = os.getenv("TO_EMAIL", "")  # Email address to receive reports (defaults to email if empty)

# Fallback: SMTP (Gmail, Outlook, etc.)
# If RESEND_API_KEY is not set, SMTP will be used with the email/password above
# For Gmail, you may need to use an App Password instead of your regular password