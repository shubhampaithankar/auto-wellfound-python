from selenium_driverless import webdriver
from selenium_driverless.types.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from config.secrets import email, password
from utils.captcha import detect_captcha

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
        print(f"Error during login: {e}")
        raise e

