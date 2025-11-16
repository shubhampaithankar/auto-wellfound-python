# Wellfound Job Application Automation

Automatically apply to jobs on Wellfound (formerly AngelList) based on your preferences.

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

```bash
# Windows
scripts\install.bat

# Linux/Mac
bash scripts/install.sh
```

Or manually:

```bash
pip install -r requirements.txt
```

### 3. Configure Settings

Edit `config/secrets.py` and add your credentials:

```python
email = "your-email@example.com"
password = "your-password"
```

Edit `config/search.py` to customize:

- `current_experience` - Your years of experience
- `good_skills` - Skills you want (e.g., "javascript", "python")
- `bad_skills` - Skills to avoid
- `strict_bad_skills` - Skills that immediately reject a job

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

### Other Filters

- Remote policy: Rejects "in office" jobs
- Experience: Rejects jobs requiring more experience than you have
- Bad words: Rejects jobs with words like "unpaid", "contractor" in description

## Notes

- The script will automatically filter jobs based on your skills and experience
- Jobs are saved to `wellfound.db` database
- Make sure Chrome/Chromium is installed
- CAPTCHA detection will pause the script if detected
- Always activate your virtual environment before running: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
