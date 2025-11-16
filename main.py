"""
Wellfound Job Application Automation Script

Copyright 2025 Shubham Paithankar

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Note: For real-time log output, you can also run this script with:
    python -u main.py
The -u flag forces unbuffered output.
"""
import asyncio
import sys
import io
import os

from selenium.common.exceptions import WebDriverException

from core.browser import initialize_browser
from core.login import login
from core.navigation import set_filters
from core.orchestrator import start_applying
from utils.captcha import detect_captcha
from services.db import initialize_database_connection, close_connection
from services.email import send_email_report
from config.settings import store_in_db, send_email, limit

# Configure stdout for real-time logging (unbuffered)
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', line_buffering=True)
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', line_buffering=True)

# Also set Python to run in unbuffered mode
os.environ['PYTHONUNBUFFERED'] = '1'

# Global variables for tracking
count = 0
applied = []
rejected = []

async def main():
    # Initialize database connection if storing in DB
    if store_in_db:
        await initialize_database_connection()

    driver = None
    try:
        # Initialize browser
        driver = await initialize_browser()
        
        # Navigate to login page
        await driver.get('https://wellfound.com/login', wait_load=True)
        await driver.sleep(2)

        # Check for CAPTCHA
        captcha = await detect_captcha(driver)
        print(f"CAPTCHA detected in main: {captcha}")
        if captcha:
            print("CAPTCHA detected, waiting for next instance of the browser...")
            return

        # Login
        await login(driver)
        await driver.sleep(2)

        # Navigate to jobs page if not already there
        if await driver.current_url != 'https://wellfound.com/jobs':
            await driver.get('https://wellfound.com/jobs', wait_load=True)
        await driver.sleep(1)

        # Set filters
        await set_filters(driver)

        # Start applying to jobs
        global count, applied, rejected
        count, applied, rejected = await start_applying(driver, applied, rejected, count, limit)

        # Send email report if enabled
        if send_email:
            await send_email_report(applied, rejected)
            
    except (WebDriverException, FileNotFoundError) as e:
        print(f"Error during main: {e}")
        if isinstance(e, FileNotFoundError) and "Chrome" in str(e):
            print("\nChrome/Chromium not found. Please:")
            print("1. Install Google Chrome or Chromium, OR")
            print("2. Specify the Chrome executable path in config/settings.py")
    finally:
        if driver is not None:
            try:
                await driver.close()
            except (AttributeError, Exception) as e:
                # Handle selenium_driverless library bug when closing
                # The script has already completed successfully, so we can safely ignore this
                print(f"Note: Error closing driver (non-critical): {type(e).__name__}")
        # Close database connection
        if store_in_db:
            await close_connection()

if __name__ == "__main__":
    asyncio.run(main())
