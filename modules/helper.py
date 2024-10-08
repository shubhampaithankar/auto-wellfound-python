from selenium_driverless import webdriver
from selenium_driverless.types.by import By
from selenium_driverless.types.webelement import WebElement
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException, NoSuchElementException
from datetime import datetime

def get_proper_string(value: str) -> str: 
    """Returns a string stripped and which maintains its idents and breaks"""
    return '\n'.join([' '.join(line.split()) for line in value.splitlines()]).strip()

async def wait_for_disappearance(driver: webdriver.Chrome, element: WebElement, timeout=3): 
    """Wait till the element is no longer displayed"""
    if await element.is_displayed():
        try: 
            await driver.sleep(timeout)
            await wait_for_disappearance(driver, element)
        except ElementNotVisibleException: 
            return
    return

async def scroll_to(driver: webdriver.Chrome, element: WebElement):
    """Scroll to given element's center"""
    try: await driver.execute_script('arguments[0].scrollIntoView({block: "center"});', element)
    except WebDriverException as e:
        raise e
    
async def detect_captcha(driver: webdriver.Chrome):
    """Detect CAPTCHA on the page."""
    try:
        captcha_element = await driver.find_element(By.XPATH, '//iframe[contains(@src, "https://geo.captcha-delivery.com/captcha")]', timeout=5)
        if captcha_element: return True
        else: return False
        # print("CAPTCHA detected, waiting for user to solve it...")

        # await wait_for_disappearance(driver, captcha_element, timeout=5)
    except: return False
 

def format_timestamp():
    # Format timestamp as dd-mm-yy:hh:mm:ss
    return datetime.now().strftime(f"%d-%m-%y:%H:%M:%S")  