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


async def login(driver: webdriver.Chrome):
    try:
        try: email_field = await driver.find_element(By.XPATH, '//input[@placeholder="Email"]', timeout=5)
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
            await login(driver)

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

async def start_applying(driver: webdriver.Chrome):
    try:
        print("Starting to apply...")
        count = 0
        limit = 2
        
        try: companies: list[WebElement] = await driver.find_elements(By.XPATH, '//div[@data-test="StartupResult"]')
        except NoSuchElementException as e:
            print("No companies found")
            raise e
        
        for company in companies:
            if count > limit: 
                print("Limit reached")
                break

            # scroll to company
            await scroll_to(driver, company)

            # hide button for the company -> bottom right
            try: hide_button = await company.find_element(By.XPATH, './/button[text()="Hide"]')
            except NoSuchElementException:
                print('Hide button not found')
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
                print("Job listing element not found")
                raise e
 
            if (len(job_listings) == 0):
                print("Zero job listings found")
                continue

            for job in job_listings:
                hide = False
                position = "Position not found"
                remote_policy = "Remote policy not found"
                compensation = "Compensation not found"
                # Check position
                try: 
                    position_dom: WebElement = await job.find_element(By.XPATH, './/span[@class="styles_title__xpQDw"]')
                    position: str = await position_dom.text

                    await driver.sleep(0.5)
                except: print(position)
            
                # Check job location
                try: 
                    location_dom: WebElement = await job.find_element(By.XPATH, './/span[@class="styles_locations__HHbZs"]')
                    remote_policy = get_proper_string(await location_dom.text)

                    if "in office" in remote_policy:
                        reason = f'{position} is not remote'
                        print(reason)
                        continue

                    await driver.sleep(0.5)
                except: print(remote_policy)

                # Check compensation
                try: 
                    compensation_dom: WebElement = await job.find_element(By.XPATH, './/span[@class="styles_compensation__3JnvU"]')
                    compensation: str = get_proper_string(await compensation_dom.text)
                    # await driver.sleep(1)
                except: print(compensation) 

                print(company_name, position, remote_policy, compensation)
            
                await job.click()

                await driver.sleep(5)
                # wait for job modal to open
                try: 
                    modal: WebElement = await driver.find_element(By.XPATH, './/div[contains(@class, "ReactModal__Content")]')
                    await driver.sleep(1)
                except: 
                    print("Modal not found")
                    continue
                
                try: 
                    close_button: WebElement = await driver.find_element(By.XPATH, '//button[@data-test="closeButton"]/*[1]')
                    await driver.sleep(1)
                except e: 
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
                        reason = 'Either already applied or not accepting from your location'
                        hide = True
                        print(reason)
                        continue

                    print("job is applicable")

                    try: skills: WebElement = await modal.find_element(By.XPATH, './/div[@class="flex flex-col gap-2"]')
                    except NoSuchElementException:
                        print("Skills not found")
                        skills = None

                    if skills:
                        await scroll_to(modal, skills)

                        skillsText = get_proper_string(await skills.text)

                        good_word = next((skill for skill in good_skills if skill.lower() in skillsText), False)
                        if good_word: print(f'Found good skill {good_word}. Skipping bad word check.')
                        else:
                            bad_word = next((skill for skill in bad_skills if skill.lower() in skillsText), False)
                            if bad_word:
                                reason = f'Found bad skill {bad_word}. Skipping.'
                                print(reason)
                                continue

                            strict_bad_word = next((skill for skill in strict_bad_skills if skill.lower() in skillsText), False)
                            if strict_bad_word:
                                reason = f'Found strict bad skill {strict_bad_word}. Skipping.'
                                print(reason)
                                continue
                    # await apply_button.click()
                    count =+ 1
                except e: 
                    print(e)
                    continue
                finally:
                    await close_button.click()
                    await driver.sleep(2)

                    # if hide:
                    #     print(reason)

    except WebDriverException as e:
        print(f"Error during start_applying {e}")
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

            # await driver.title

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