from selenium_driverless import webdriver
from selenium_driverless.types.webelement import WebElement
from selenium_driverless.types.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from utils.helpers import wait_for_disappearance

async def set_filters(driver: webdriver.Chrome):
    try:
        try: sort_by = await driver.find_element(By.XPATH, '//button/span[text()="Recommended"]', timeout=15)
        except NoSuchElementException as e:
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

