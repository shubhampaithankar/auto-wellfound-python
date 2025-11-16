# Wellfound Job Application Automation

Automatically apply to jobs on Wellfound (formerly AngelList) based on your preferences.

**Copyright (c) 2025 Shubham Paithankar**

Licensed under the Apache License 2.0 - see [LICENSE](LICENSE) file for details.

## Quick Start

### 1. Setup Virtual Environment (Recommended)

```bash
# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 2. Install Dependencies

The installation scripts will automatically:

- Create a virtual environment (`venv/`)
- Install all packages **locally in the venv** (not globally)
- Set up configuration files

```bash
# Windows
scripts\install.bat

# Linux/Mac
bash scripts/install.sh
```

Or manually (make sure venv is activated first):

```bash
pip install -r requirements.txt
```

### 3. Configure Settings

Create a `.env` file in the project root (or copy from `.env.example` if it exists) and add your credentials:

```env
WELLFOUND_EMAIL=your-email@example.com
WELLFOUND_PASSWORD=your-password
```

Edit `config/search.py` to customize:

- `current_experience` - Your years of experience (used to filter jobs)
- `good_skills` - Skills you want (e.g., "javascript", "python")
- `bad_skills` - Skills to avoid
- `strict_bad_skills` - Skills that immediately reject a job
- `bad_words` - Words in job description that cause rejection (e.g., "unpaid", "contractor")

**Skills Algorithm:**

- If a **good skill** is found → job passes (no bad skills check)
- If no good skill found → check **bad skills** (if found, reject)
- **Strict bad skills** are **always checked** regardless of good skills
- If strict bad skill found → always reject

Edit `config/settings.py`:

- `headless = False` - Set to `True` to run browser in background
- `store_in_db = True` - Save jobs to database
- `send_email = False` - Send email report when done
- `hide_companies = False` - Hide companies after processing
- `limit = 5` - Number of jobs to apply to (set to `0` for unlimited)

### 4. Run

```bash
# Windows
.\run.bat

# Linux/Mac
bash run.sh

# Or directly
python main.py
```

## Email Reports

The script can send email reports with a CSV attachment of all applied/rejected jobs.

### Setup Email Service

1. **Option 1: Resend API (Recommended - FREE 3,000 emails/month)**

   - Sign up at [resend.com](https://resend.com)
   - Get your API key
   - Add to `.env` file:
     ```env
     RESEND_API_KEY=your-api-key-here
     ```

2. **Option 2: SMTP (Gmail)**

   - Uses your Wellfound login credentials from `.env`
   - Requires Gmail App Password (not regular password) if using Gmail
   - Enable 2FA and create App Password: https://myaccount.google.com/apppasswords
   - Update `WELLFOUND_PASSWORD` in `.env` with the App Password

3. **Configure Email Addresses** (optional, in `.env` file):

   ```env
   FROM_EMAIL=sender@example.com  # Optional, defaults to your login email
   TO_EMAIL=recipient@example.com  # Optional, defaults to your login email
   ```

4. **Enable Email Reports** (in `config/settings.py`):
   ```python
   send_email = True
   ```

The email includes:

- Summary (applied/rejected counts)
- CSV attachment with all job details

## View Database

To see all applied/rejected jobs:

```bash
python scripts/view_db.py
```

## Project Structure

```
├── main.py              # Entry point
├── core/                # Automation logic
├── utils/               # Helper functions
├── services/            # Database & email
├── config/              # Settings & credentials
└── scripts/             # Utility scripts
```

## How It Works

### Skills Filtering Logic

1. **Good Skills Check**: If any good skill is found, the job passes this check
2. **Strict Bad Skills Check**: Always checked regardless of good skills - if found, job is rejected
3. **Bad Skills Check**: Only checked if no good skill was found - if found, job is rejected

Example:

- Job has "javascript" (good) and "java" (bad) → **Passes** (good skill found, bad skills ignored)
- Job has "javascript" (good) and ".net" (strict bad) → **Rejected** (strict bad always checked)
- Job has "java" (bad) but no good skills → **Rejected** (bad skill found)

### Description & Bad Words Filter

After skills pass, the script checks the job description:

1. **Experience Check**: Extracts experience requirements from:

   - Job title (e.g., "Senior Developer (5+ years)")
   - Job description text
   - Requirements list in the modal

   - Rejects if job requires more experience than `current_experience`
   - Handles formats like "2 years", "3-5 years", "5+ years"

2. **Bad Words Check**: Scans the entire job description for words in `bad_words` list
   - If any bad word found → job is rejected
   - Example: Job with "unpaid internship" → rejected

### Other Filters

- **Remote policy**: Rejects jobs with "in office" in location/remote policy
- **Position check**: Rejects if position title cannot be found
- **Compensation check**: Rejects if compensation info cannot be found

## Notes

- The script will automatically filter jobs based on your skills and experience
- Jobs are saved to `wellfound.db` database
- Make sure Chrome/Chromium is installed
- CAPTCHA detection will pause the script if detected
- Always activate your virtual environment before running: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
- Installation scripts install packages **locally in venv**, not globally
- Use the provided run scripts (`.bat`, `.ps1`, `.sh`) - they handle venv activation automatically
