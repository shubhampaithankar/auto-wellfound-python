import asyncio
import sys
import io
import re

from selenium_driverless import webdriver
from selenium_driverless.types.webelement import WebElement
from selenium_driverless.types.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, ElementNotVisibleException

from modules.helper import *

from config.search import *
from config.secrets import *


sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

count = 0
limit = 15
reason = ""

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

                # await process_jobs(driver, job_listings, company_name)

                # hide company
                await hide_button.click()

                try: 
                    hide_input: WebElement = await company.find_element(By.XPATH,'//input[@name="hideReason"]', timeout=10)
                    hide_confirm: WebElement = await company.find_element(By.XPATH,'//span[@class="fill-current stroke-current w-3 leading-none"]', timeout=10)
                except: 
                    print(f"Hide button not found")
                    continue

                await hide_input.clear()
                await driver.sleep(0.5)

                try:
                    await hide_input.send_keys(reason)
                    await driver.sleep(0.5)
                except: print('Unable to fill in hide reason')

                await hide_confirm.click()
                await driver.sleep(1) 

            try:
                companies.clear()
                await driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await driver.sleep(3)
                return await start_applying(driver)
            except WebDriverException as e: 
                print(f"Error during more load_companies")
                raise e
        
    except WebDriverException as e:
        print(f"Error during start_applying")
        raise e


async def main():
    options = webdriver.ChromeOptions()
    # options.add_argument("--incognito")

    headless = False

    if not headless:
        dark_reader = 'extension/dark-reader.zip'
        options.add_extension(dark_reader)

    async with webdriver.Chrome(options=options) as driver:
        try:
            await driver.maximize_window()
            await driver.sleep(1)

            await driver.get('https://wellfound.com/login', wait_load=True)
            await driver.sleep(2)


            await login(driver)

            if await driver.current_url != 'https://wellfound.com/jobs':
                await driver.get('https://wellfound.com/jobs', wait_load=True)
            await driver.sleep(1)

            await set_filters(driver)

            await start_applying(driver)
        except WebDriverException as e:
            print(f"Error during main: {e}")
        finally:
            await driver.close()

asyncio.run(main())