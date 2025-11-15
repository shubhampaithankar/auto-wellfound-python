import os
import csv
import smtplib
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from datetime import datetime

from config.secrets import resend_api_key, from_email, to_email, email, password


async def send_email_report(applied: list, rejected: list):
    """
    Send email report with CSV attachment containing job application data.
    
    Args:
        applied: List of applied job dictionaries
        rejected: List of rejected job dictionaries
    """
    try:
        if len(applied) == 0 and len(rejected) == 0:
            print("No jobs to report. Skipping email.")
            return
        
        # Create CSV file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        csv_filename = f"job_report_{timestamp}.csv"
        
        # Define CSV columns
        fieldnames = [
            'status', 'company_name', 'position', 'remote_policy', 'compensation',
            'location', 'type', 'exp_required', 'skills', 'url', 
            'application_date', 'time', 'notes'
        ]
        
        # Write CSV file
        with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            
            # Write applied jobs
            for job in applied:
                writer.writerow({
                    'status': 'applied',
                    'company_name': job.get('company_name', ''),
                    'position': job.get('position', ''),
                    'remote_policy': job.get('remote_policy', ''),
                    'compensation': job.get('compensation', ''),
                    'location': job.get('location', ''),
                    'type': job.get('type', ''),
                    'exp_required': job.get('exp_required', ''),
                    'skills': job.get('skills', ''),
                    'url': job.get('url', ''),
                    'application_date': job.get('application_date', ''),
                    'time': job.get('time', ''),
                    'notes': job.get('notes', '')
                })
            
            # Write rejected jobs
            for job in rejected:
                writer.writerow({
                    'status': 'rejected',
                    'company_name': job.get('company_name', ''),
                    'position': job.get('position', ''),
                    'remote_policy': job.get('remote_policy', ''),
                    'compensation': job.get('compensation', ''),
                    'location': job.get('location', ''),
                    'type': job.get('type', ''),
                    'exp_required': job.get('exp_required', ''),
                    'skills': job.get('skills', ''),
                    'url': job.get('url', ''),
                    'application_date': job.get('application_date', ''),
                    'time': job.get('time', ''),
                    'notes': job.get('notes', '')
                })
        
        print(f"CSV report created: {csv_filename}")
        
        # Determine email addresses
        sender_email = from_email if from_email else email
        recipient = to_email if to_email else email
        
        email_sent = False
        
        # Try Resend API first (FREE - 3,000 emails/month)
        if resend_api_key:
            try:
                import requests
                
                # Read CSV file content
                with open(csv_filename, 'rb') as f:
                    csv_content = f.read()
                
                # Resend API endpoint
                url = "https://api.resend.com/emails"
                
                # Prepare email data
                email_data = {
                    "from": sender_email,
                    "to": [recipient],
                    "subject": f"Job Application Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
                    "text": f"""Job Application Report

Summary:
- Applied: {len(applied)} jobs
- Rejected: {len(rejected)} jobs
- Total: {len(applied) + len(rejected)} jobs

Please find the detailed CSV report attached.""",
                    "attachments": [{
                        "filename": csv_filename,
                        "content": base64.b64encode(csv_content).decode('utf-8')
                    }]
                }
                
                headers = {
                    "Authorization": f"Bearer {resend_api_key}",
                    "Content-Type": "application/json"
                }
                
                response = requests.post(url, json=email_data, headers=headers)
                response.raise_for_status()
                print(f"Email report sent successfully via Resend to {recipient}")
                email_sent = True
                
            except ImportError:
                print("Error: 'requests' package is required for Resend. Install it with: pip install requests")
                print("Falling back to SMTP...")
            except Exception as e:
                print(f"Error sending email via Resend: {e}")
                print("Falling back to SMTP...")
        
        # Fallback to SMTP if Resend is not configured or failed
        if not email_sent:
            # Create email message
            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = recipient
            msg['Subject'] = f"Job Application Report - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            # Email body
            body = f"""
            Job Application Report
            
            Summary:
            - Applied: {len(applied)} jobs
            - Rejected: {len(rejected)} jobs
            - Total: {len(applied) + len(rejected)} jobs
            
            Please find the detailed CSV report attached.
            """
            msg.attach(MIMEText(body, 'plain'))
            
            # Attach CSV file
            with open(csv_filename, 'rb') as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header(
                    'Content-Disposition',
                    f'attachment; filename= {csv_filename}'
                )
                msg.attach(part)
            
            # Send email using SMTP
            try:
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email, password)
                text = msg.as_string()
                server.sendmail(sender_email, recipient, text)
                server.quit()
                print(f"Email report sent successfully via SMTP to {recipient}")
            except Exception as e:
                print(f"Error sending email: {e}")
                print("Note: If using Gmail, you may need to:")
                print("1. Enable 'Less secure app access' OR")
                print("2. Use an App Password instead of your regular password")
                raise e
        
        # Clean up CSV file
        try:
            if os.path.exists(csv_filename):
                os.remove(csv_filename)
                print(f"Temporary CSV file {csv_filename} removed")
        except Exception as e:
            print(f"Warning: Could not remove temporary CSV file: {e}")
                
    except Exception as e:
        print(f"Error in send_email_report: {e}")
        raise e

