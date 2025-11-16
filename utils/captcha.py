from selenium_driverless import webdriver
from selenium_driverless.types.by import By

async def detect_captcha(driver: webdriver.Chrome):
    """Detect CAPTCHA on the page."""
    try:
        captcha_element = await driver.find_element(By.XPATH, '//iframe[contains(@src, "https://geo.captcha-delivery.com/captcha")]', timeout=5)
        if captcha_element: return True
        else: return False
        # print("CAPTCHA detected, waiting for user to solve it...")

        # await wait_for_disappearance(driver, captcha_element, timeout=5)
    except: return False

