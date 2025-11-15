email="shubhampaithankar65@gmail.com"
password="REMOVED"

# Email service configuration (optional - leave empty to use SMTP)
# Option 1: Use SendGrid (recommended - free tier available)
# Get API key from: https://app.sendgrid.com/settings/api_keys
sendgrid_api_key=""  # e.g., "SG.xxxxxxxxxxxxx"
from_email=""  # Email address to send from (can be different from login email)
to_email=""  # Email address to receive reports (defaults to email if empty)

# Option 2: Use SMTP (Gmail, Outlook, etc.)
# If sendgrid_api_key is empty, SMTP will be used with the email/password above

mysql_host="localhost"
mysql_port=3306
mysql_user="root"
mysql_password=""
mysql_database=""