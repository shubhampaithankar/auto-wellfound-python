import asyncio

from selenium_driverless import webdriver
from selenium_driverless.types.by import By

from config.secrets import *

async def main():
    options = webdriver.ChromeOptions()
    options.add_argument("--incognito")
    options.add_argument("--disable-extensions")

    async with webdriver.Chrome(options=options) as driver:

        await driver.maximize_window()

        await driver.get('https://wellfound.com/login', wait_load=True)
        await driver.sleep(0.5)

        try:
            email_field = await driver.find_element(By.XPATH, '//input[@placeholder="Email"]', timeout=10)
            print('Email field found')

            print('Filling email field')
            await email_field.clear()
            await email_field.send_keys(email)  # Add your email here

            password_field = await driver.find_element(By.XPATH, '//input[@placeholder="Password"]')
            print('Password field found')

            print('Filling password field')
            await password_field.clear()
            await password_field.send_keys(password)  # Add your password here
            
            submit_button = await driver.find_element(By.XPATH, '//input[@value="Log in"]')
            await submit_button.click()

            await driver.wait_for_cdp('Page.loadEventFired', timeout=15)

            # await set_filters(driver)
            print('Filters set')

            # await start_applying(driver)
        except Exception as e:
            print(e)
        finally:
            await driver.close()

asyncio.run(main())