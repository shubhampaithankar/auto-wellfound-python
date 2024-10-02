import asyncio

from selenium_driverless import webdriver
from selenium_driverless.types.by import By
from selenium.common.exceptions import NoSuchElementException

from config.secrets import *

async def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")

    async with webdriver.Chrome(options=options) as driver:
        try:
            await driver.maximize_window()

            await driver.get('https://wellfound.com/login', wait_load=True)

            try: email_field = await driver.find_element(By.XPATH, '//input[@placeholder="Email"]', timeout=5)
            except NoSuchElementException: 
                print("Email field not found")
                return

            await email_field.clear()
            await email_field.send_keys(email)

            await driver.sleep(0.5)

            try: password_field = await driver.find_element(By.XPATH, '//input[@placeholder="Password"]', timeout=5)
            except NoSuchElementException: 
                print("Password field not found")
                return

            await password_field.clear()
            await password_field.send_keys(password)

            await driver.sleep(0.5)
            
            try: submit_button = await driver.find_element(By.XPATH, '//input[@value="Log in"]', timeout=5)
            except NoSuchElementException:
                print("Submit button not found")
                return
            
            await submit_button.click()

            await driver.wait_for_cdp('Page.loadEventFired', timeout=15)

            # await set_filters(driver)
            print('Filters set')

            # await start_applying(driver)
        except Exception as e:
            print(f"Error during main: {e}")
        finally:
            await driver.close()

asyncio.run(main())