import asyncio
import sys
import io
import re
import os

from selenium_driverless import webdriver
from selenium_driverless.types.webelement import WebElement
from selenium_driverless.types.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from dotenv import load_dotenv

from modules.helper import *
from modules.db import *

from config.settings import *
from config.search import *
from config.secrets import *

load_dotenv()

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

count = 0
limit = 5
reason = ""

applied = []
rejected = []

async def login(driver: webdriver.Chrome, retries=3):
    try:
        try: email_field = await driver.find_element(By.XPATH, '//input[@placeholder="Email"]', timeout=15)
        except NoSuchElementException as e: 
            print("Email field not found")
            raise e

        await email_field.clear()
        await email_field.send_keys(email)

        await driver.sleep(1)

        try: password_field = await driver.find_element(By.XPATH, '//input[@placeholder="Password"]', timeout=5)
        except NoSuchElementException as e: 
            print("Password field not found")
            raise e

        await password_field.clear()
        await password_field.send_keys(password)

        await driver.sleep(1)
        
        try: submit_button = await driver.find_element(By.XPATH, '//input[@value="Log in"]', timeout=5)
        except NoSuchElementException as e:
            print("Submit button not found")
            raise e 
        
        await submit_button.click()
        await driver.sleep(5)

        captcha = await detect_captcha(driver)
        print(f"CAPTCHA detected in login: {captcha}")
        if captcha:
            print("CAPTCHA detected, waiting for next instance of the browser...")
            return

        try: await driver.get('https://wellfound.com/jobs', wait_load=True)
        except WebDriverException as e:
            print(f"Error during redirect to jobs page: {e}")
            raise e

        # wait till redirect to jobs page
        if await driver.current_url != 'https://wellfound.com/jobs':
            if retries > 0:
                print("Login failed, retrying...")
                return await login(driver, retries=retries - 1)
            else:
                raise WebDriverException("Failed to login after multiple attempts")

        await driver.sleep(1)

    except WebDriverException as e:
        print(f"Error during setting filters: {e}")
        raise e

async def set_filters(driver: webdriver.Chrome):
    try:
        try: sort_by = await driver.find_element(By.XPATH, '//button/span[text()="Recommended"]', timeout=15)
        except NoSuchElementException:
            print("Sort button not found")
            raise e

        await sort_by.click()
        await driver.sleep(1)

        try: most_recent = await driver.find_element(By.XPATH, '//span[text()="See most recent jobs first"]')
        except NoSuchElementException:
            print("Most Recent option not found")
            raise e

        await most_recent.click()

        try: loader: WebElement = await driver.find_element(By.XPATH, '//div[@class="styles_component__YafBz"]', timeout=10)
        except NoSuchElementException:
            print("Loader div not found")

        await wait_for_disappearance(driver, loader)
        await driver.sleep(1)

    except WebDriverException as e:
        print(f"Error during setting filters: {e}")
        raise e

async def load_companies(driver: webdriver.Chrome):
    try: companies: list[WebElement] = await driver.find_elements(By.XPATH, '//div[@data-test="StartupResult"]')
    except NoSuchElementException as e:
        print("No companies found")
        return []
    return companies

async def process_jobs(driver: webdriver.Chrome, job_listings: list[WebElement], company_name: str):
    try:
        global count, reason, applied, rejected
        for job in job_listings:
            position = "Position not found"
            remote_policy = "Remote policy not found"
            compensation = "Compensation not found"
            time = format_timestamp()

            # job object to store
            job_obj = {
                'company_name': company_name,
                'position': position,
                'remote_policy': remote_policy,
                'compensation': compensation,
                'time': time,
                'url': None,
                'type': None,
                'location': None,
                'exp_required': None,
                'application_date': None
            }

            # Check position
            try: 
                position_dom: WebElement = await job.find_element(By.XPATH, './/span[@class="styles_title__xpQDw"]')
                position: str = await position_dom.text
                job_obj['position'] = position

                await driver.sleep(0.5)
            except: 
                reason = f"{position}"
                continue
        
            # Check job location
            try: 
                location_dom: WebElement = await job.find_element(By.XPATH, './/span[@class="styles_locations__HHbZs"]')
                remote_policy = get_proper_string(await location_dom.text)
                job_obj['remote_policy'] = remote_policy
                job_obj['location'] = remote_policy  # Store location as well

                if "in office" in remote_policy.lower():
                    reason = f'{position} is not remote'
                    continue

                await driver.sleep(0.5)
            except:                     
                reason = f"{remote_policy}"
                continue

            # Check compensation
            try: 
                compensation_dom: WebElement = await job.find_element(By.XPATH, './/span[@class="styles_compensation__3JnvU"]')
                compensation: str = get_proper_string(await compensation_dom.text)
                job_obj['compensation'] = compensation
                # await driver.sleep(1)
            except:                     
                reason = f"{compensation}"
                continue
        
            await job.click()
            # await driver.sleep(3)
            # wait for job modal to open
            try: 
                modal: WebElement = await driver.find_element(By.XPATH, './/div[contains(@class, "ReactModal__Content")]', timeout=15)
                await driver.sleep(1)
            except: 
                print("Modal not found")
                continue

            try: 
                close_button: WebElement = await driver.find_element(By.XPATH, '//button[@data-test="closeButton"]/*[1]')
                await driver.sleep(1)
            except: 
                print("Modal close button not found")
                continue
            
            try:
                try: 
                    apply_button: WebElement = await modal.find_element(By.XPATH, '//div[@class="styles_component__AUM9C flex flex-row justify-end"]/*[1]')
                    await driver.sleep(1)
                except: 
                    print("Apply button not found")
                    continue

                if await apply_button.get_attribute('disabled'):
                    reason = f"Either already applied or not accepting from location"
                    continue

                try: 
                    skills: WebElement = await modal.find_element(By.XPATH, './/div[@class="flex flex-col gap-2"]')
                except:
                    print("Skills not found")
                    skills = None

                if skills:
                    await scroll_to(modal, skills)

                    skillsText = get_proper_string(await skills.text)
                    job_obj['skills'] = skillsText

                    skills_low = skillsText.lower()

                    good_word = next((skill for skill in good_skills if skill.lower() in skills_low), False)
                    if not good_word:
                        bad_word = next((skill for skill in bad_skills if skill.lower() in skills_low), False)
                        if bad_word:
                            reason = f'Found bad skill {bad_word}. Skipping.'
                            continue


                    strict_bad_word = next((skill for skill in strict_bad_skills if skill.lower() in skills_low), False)
                    if strict_bad_word:
                        reason = f'Found strict bad skill {strict_bad_word}. Skipping.'
                        continue
                
                # check for required experience & bad words
                try: description_dom: WebElement = await modal.find_element(By.XPATH, '//div[@id="job-description"]')
                except: 
                    print("Description not found")
                    continue

                await scroll_to(modal, description_dom)

                description = get_proper_string(await description_dom.text)
                job_obj['description'] = description

                desc_low = description.lower()

                required_experience = re.compile(r'(?:\(\s*(\d+)\s*\)|(\d+))?\s*[-to]*\s*(\d+)?\+?\s*(year|yr)s?', re.IGNORECASE)
                match = required_experience.search(desc_low)

                if match:
                    lower_limit = int(match.group(1) or match.group(2) or 0)
                    upper_limit = int(match.group(3)) if match.group(3) else current_experience
                    exp_text = f"{lower_limit}-{upper_limit} years" if match.group(3) else f"{lower_limit}+ years"
                    job_obj['exp_required'] = exp_text

                    if not lower_limit <= current_experience <= upper_limit:
                        reason = f"Not enough experience"
                        continue
                else:
                    job_obj['exp_required'] = None
                
                skip = False
                for word in bad_words:
                    if word.lower() in desc_low:
                        reason = f"Skipped job due to bad word {word} found in description"
                        skip = True
                        break
                if skip: continue
                
                # Get job URL from current page
                try:
                    job_url = await driver.current_url
                    job_obj['url'] = job_url
                except:
                    job_obj['url'] = None

                # Try to get job type (Full-time, Part-time, etc.)
                try:
                    # Look for job type in the modal
                    type_elements = await modal.find_elements(By.XPATH, './/span[contains(text(), "Full-time") or contains(text(), "Part-time") or contains(text(), "Contract") or contains(text(), "Internship")]')
                    if type_elements:
                        job_obj['type'] = await type_elements[0].text
                    else:
                        job_obj['type'] = None
                except:
                    job_obj['type'] = None

                try: 
                    text_area: WebElement = await modal.find_element(By.XPATH, '//textarea[contains(@id, "form-input")]')
                    await text_area.clear()
                    await text_area.send_keys(f"Hello! I'd like to apply for the {position} role at {company_name}.")
                except: print("Text area not found")

                # Set application date when actually applying
                job_obj['application_date'] = format_timestamp()

                await apply_button.click()
                applied.append(job_obj)
                count += 1
            except WebDriverException as e:
                print(e)
                job_obj['notes'] = reason
                rejected.append(job_obj)
                continue
            finally:
                if await close_button.is_visible():
                    await close_button.click()
                    await driver.sleep(1)
                else: return
                
    except WebDriverException as e:
        print("error in process_jobs")
        raise e

async def hide_company(driver: webdriver.Chrome, hide_button: WebElement, company: WebElement):
    try:
        global reason
        await hide_button.click()
        try: 
            hide_input: WebElement = await company.find_element(By.XPATH,'//input[@name="hideReason"]', timeout=10)
            hide_confirm: WebElement = await company.find_element(By.XPATH,'//span[@class="fill-current stroke-current w-3 leading-none"]', timeout=10)
        except: 
            print(f"Hide button not found")
            return False

        await hide_input.clear()
        await driver.sleep(0.5)

        try:
            await hide_input.send_keys(reason)
            await driver.sleep(0.5)
        except: print('Unable to fill in hide reason')

        await hide_confirm.click()
        await driver.sleep(1)
        
        return True
    except: print('Unable to hide company')

async def start_applying(driver: webdriver.Chrome):
    try:
        print("Starting to apply...")

        global count, limit, reason
        
        while count < limit:
            companies = await load_companies(driver)
            if len(companies) == 0:
                print(f"No companies found")
                return
            
            for company in companies:

                if count > limit:
                    print("Limit reached")
                    break
                
                reason = "applied"

                # scroll to company
                await scroll_to(driver, company)

                # hide button for the company -> bottom right
                try: hide_button: WebElement = await company.find_element(By.XPATH, './/button[text()="Hide"]')
                except NoSuchElementException:
                    print(f"Hide button not found") 
                    continue
                
                try: 
                    company_name_dom: WebElement = await company.find_element(By.XPATH, './/h2[@class="inline text-md font-semibold"]')
                    company_name: str = await company_name_dom.text

                    await driver.sleep(0.5)
                except NoSuchElementException as e:
                    print(f"Company name not found")
                    continue

                # get jobs listed by the company
                try: job_listings: list[WebElement] = await company.find_elements(By.XPATH, ".//div[@class='styles_component__Ey28k']")   
                except NoSuchElementException as e:
                    print(f"Job listing element not found")
                    raise e
    
                if (len(job_listings) == 0):
                    reason = f"Zero job listings found"
                    continue

                await process_jobs(driver, job_listings, company_name)

                # hide company
                if (hide_companies):
                    await hide_company(driver, hide_button, company)

            try:
                companies.clear()
                await driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await driver.sleep(3)
                return await start_applying(driver)
            except WebDriverException as e: 
                print(f"Error during more load_companies")
                raise e
            
        print("Finished applying")
        print("---------------------------------------")
        print(f"Applied: {len(applied)}")
        print(f"Rejected: {len(rejected)}")
        print("---------------------------------------")

        return
        
    except WebDriverException as e:
        print(f"Error during start_applying")
        raise e

async def store_jobs():
    try:
        # Create SQLite connection
        conn = await get_sqlite_connection()
        if not conn: 
            print("Failed to establish database connection.")
            return

        # Initialize counters
        applied_count = 0
        rejected_count = 0

        global applied, rejected

        try:
            # Initialize database table
            await init_database(conn)

            # Prepare query for inserting jobs (SQLite uses ? placeholders)
            query = """
                INSERT INTO job_applications 
                (company_name, position, remote_policy, compensation, skills, description, status, notes, url, type, location, exp_required, application_date, time) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """

            # Store applied jobs
            for job in applied:
                data = (
                    job.get('company_name', 'Unknown Company'),  # Use fallback value
                    job.get('position', 'Unknown Position'),     # Use fallback value
                    job.get('remote_policy', None),
                    job.get('compensation', None),
                    job.get('skills', None),
                    job.get('description', None),
                    'applied',  # status
                    None,  # notes is null for applied jobs
                    job.get('url', None),
                    job.get('type', None),
                    job.get('location', None),
                    job.get('exp_required', None),
                    job.get('application_date', None),
                    job.get('time'),  # timestamp when job was processed
                )
                await conn.execute(query, data)
                applied_count += 1

            # Store rejected jobs
            for job in rejected:
                data = (
                    job.get('company_name', 'Unknown Company'),  # Use fallback value
                    job.get('position', 'Unknown Position'),     # Use fallback value
                    job.get('remote_policy', None),
                    job.get('compensation', None),
                    job.get('skills', None),
                    job.get('description', None),
                    'rejected',  # status
                    job.get('notes', None),  # notes for rejection reason
                    job.get('url', None),
                    job.get('type', None),
                    job.get('location', None),
                    job.get('exp_required', None),
                    job.get('application_date', None),  # null for rejected jobs
                    job.get('time'),  # timestamp when job was processed
                )
                await conn.execute(query, data)
                rejected_count += 1

            # Commit all changes
            await conn.commit()
            print(f"Stored {applied_count} applied jobs and {rejected_count} rejected jobs in the database.")

        finally:
            # Close the database connection
            await conn.close()

    except Exception as e:
        print(f"Error storing jobs in the database: {e}")
        raise e

async def send_email_report():
    try: return
    except Exception as e:
        raise e

async def main():
    options = webdriver.ChromeOptions()

    # Set Chrome executable path if specified in settings
    if chrome_path and os.path.exists(chrome_path):
        options.binary_location = chrome_path
    elif chrome_path:
        print(f"Warning: Specified Chrome path '{chrome_path}' does not exist. Attempting auto-detect...")

    if not headless:
        dark_reader = 'extension/dark-reader.zip'
        if os.path.exists(dark_reader):
            options.add_extension(dark_reader)
        else:
            print(f"Warning: Extension file '{dark_reader}' not found. Continuing without Dark Reader extension.")
    else:
        options.add_argument("--headless")
        options.add_argument("--incognito")

    driver = None
    try:
        driver = await webdriver.Chrome(options=options)
        await driver.maximize_window()
        await driver.sleep(1)

        await driver.get('https://wellfound.com/login', wait_load=True)
        await driver.sleep(2)

        captcha = await detect_captcha(driver)
        print(f"CAPTCHA detected in main: {captcha}")
        if captcha:
            print("CAPTCHA detected, waiting for next instance of the browser...")
            return

        await login(driver)
        await driver.sleep(2)

        if await driver.current_url != 'https://wellfound.com/jobs':
            await driver.get('https://wellfound.com/jobs', wait_load=True)
        await driver.sleep(1)

        await set_filters(driver)

        await start_applying(driver)

        if store_in_db: await store_jobs()

        if send_email: await send_email_report()
    except (WebDriverException, FileNotFoundError) as e:
        print(f"Error during main: {e}")
        if isinstance(e, FileNotFoundError) and "Chrome" in str(e):
            print("\nChrome/Chromium not found. Please:")
            print("1. Install Google Chrome or Chromium, OR")
            print("2. Specify the Chrome executable path in config/settings.py")
    finally:
        if driver is not None:
            await driver.close()

asyncio.run(main())