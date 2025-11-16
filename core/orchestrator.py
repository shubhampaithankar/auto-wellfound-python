from selenium_driverless import webdriver
from selenium_driverless.types.webelement import WebElement
from selenium_driverless.types.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium_driverless.types.webelement import NoSuchElementException as DriverlessNoSuchElementException
from core.navigation import load_companies
from core.job_processor import process_jobs
from core.application import hide_company
from utils.helpers import scroll_to
from config.settings import hide_companies

async def start_applying(driver: webdriver.Chrome, applied: list, rejected: list, count: int, limit: int):
    """
    Main orchestration function that coordinates the job application process.
    
    Returns:
        tuple: (updated_count, updated_applied, updated_rejected)
    """
    try:
        print("Starting to apply...")
        
        # If limit is 0, run unlimited until no more jobs
        while limit == 0 or count < limit:
            companies = await load_companies(driver)
            if len(companies) == 0:
                print(f"No companies found")
                return count, applied, rejected
            
            for company in companies:

                if company is False:
                    await driver.sleep(2)
                    if company is False:
                        continue

                if limit > 0 and count >= limit:
                    print("Limit reached")
                    break
                
                reason = "applied"

                # scroll to company
                await scroll_to(driver, company)
                await driver.sleep(2)

                # hide button for the company -> bottom right
                try: 
                    hide_button: WebElement = await company.find_element(By.XPATH, './/button[normalize-space(text())="Hide"]')
                except (NoSuchElementException, DriverlessNoSuchElementException):
                    print(f"Hide button not found, moving to next company") 
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
                    print(f"Job listing element not found")
                    raise e
    
                if (len(job_listings) == 0):
                    reason = f"Zero job listings found"
                    continue

                count = await process_jobs(driver, job_listings, company_name, applied, rejected, count, limit)

                # hide company
                if (hide_companies):
                    await hide_company(driver, hide_button, company, reason)

            try:
                companies.clear()
                await driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                await driver.sleep(3)
                return await start_applying(driver, applied, rejected, count, limit)
            except WebDriverException as e: 
                print(f"Error during more load_companies")
                raise e
            
        print("Finished applying")
        print("---------------------------------------")
        print(f"Applied: {len(applied)}")
        print(f"Rejected: {len(rejected)}")
        print("---------------------------------------")

        return count, applied, rejected
        
    except WebDriverException as e:
        print(f"Error during start_applying")
        raise e

