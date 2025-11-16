from selenium_driverless import webdriver
from selenium_driverless.types.webelement import WebElement
from selenium_driverless.types.by import By

async def hide_company(driver: webdriver.Chrome, hide_button: WebElement, company: WebElement, reason: str):
    try:
        await hide_button.click()
        try: 
            hide_input: WebElement = await company.find_element(By.XPATH,'//input[@name="hideReason"]', timeout=10)
            hide_confirm: WebElement = await company.find_element(By.XPATH,'//span[@class="fill-current stroke-current w-3 leading-none"]', timeout=10)
        except: 
            print(f"Hide button not found")
            return False

        await hide_input.clear()
        await driver.sleep(0.5)

        try:
            await hide_input.send_keys(reason)
            await driver.sleep(0.5)
        except: print('Unable to fill in hide reason')

        await hide_confirm.click()
        await driver.sleep(1)
        
        return True
    except: 
        print('Unable to hide company')
        return False

