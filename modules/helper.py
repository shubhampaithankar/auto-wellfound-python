from selenium_driverless import webdriver
from selenium_driverless.types.webelement import WebElement
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException

def get_proper_string(value: str) -> str: 
    return '\n'.join([' '.join(line.split()) for line in value.splitlines()]).strip().lower()

async def wait_for_disappearance(driver: webdriver.Chrome, element: WebElement): 
    if await element.is_displayed():
        try: 
            await driver.sleep(3)
            await wait_for_disappearance(driver, element)
        except ElementNotVisibleException: 
            return
    return

async def scroll_to(driver: webdriver.Chrome, element: WebElement):
    try: await driver.execute_script('arguments[0].scrollIntoView({block: "center"});', element)
    except WebDriverException as e:
        raise e
    