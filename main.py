import asyncio

from selenium_driverless import webdriver
from selenium_driverless.types.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException

from config.secrets import *

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

    except WebDriverException as e:
        print(f"Error during setting filters: {e}")
        raise e

async def set_filters(driver: webdriver.Chrome):
    try:
        try: sort = await driver.find_element(By.XPATH, '//button/span[text()="Recommended"]', timeout=15)
        except NoSuchElementException:
            print("Sort button not found")
            raise e

        await sort.click()
        await driver.sleep(1)

        try: options = await driver.find_element(By.XPATH, '//div[@id="tippy-11"]', timeout=15)
        except NoSuchElementException:
            print("Options not found")
            raise e

        await options.click()
        await driver.sleep(1)

        try: most_recent = await driver.find_element(By.XPATH, '//div[contains(text(), "Most Recent")]', timeout=15)
        except NoSuchElementException:
            print("Most Recent option not found")
            raise e

        await driver.sleep(1)
        await most_recent.click()
    except WebDriverException as e:
        print(f"Error during setting filters: {e}")
        raise e

async def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")

    async with webdriver.Chrome(options=options) as driver:
        try:
            await driver.maximize_window()

            await driver.get('https://wellfound.com/login', wait_load=True)

            await login(driver)

            if await driver.current_url != 'https://wellfound.com/jobs':
                await login(driver)

            await driver.sleep(1)

            if await driver.current_url != 'https://wellfound.com/jobs':
                await driver.get('https://wellfound.com/jobs', wait_load=True)

            await set_filters(driver)

            await driver.sleep(1)

            # await start_applying(driver)
        except WebDriverException as e:
            print(f"Error during main: {e}")
        finally:
            await driver.close()

asyncio.run(main())