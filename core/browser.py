import os
from selenium_driverless import webdriver
from config.settings import headless, chrome_path

def create_browser_options() -> webdriver.ChromeOptions:
    """Create and configure Chrome browser options."""
    options = webdriver.ChromeOptions()

    # Set Chrome executable path if specified in settings
    if chrome_path and os.path.exists(chrome_path):
        options.binary_location = chrome_path
    elif chrome_path:
        print(f"Warning: Specified Chrome path '{chrome_path}' does not exist. Attempting auto-detect...")

    if not headless:
        dark_reader = 'extension/dark-reader.zip'
        if os.path.exists(dark_reader):
            options.add_extension(dark_reader)
        else:
            print(f"Warning: Extension file '{dark_reader}' not found. Continuing without Dark Reader extension.")
    else:
        options.add_argument("--headless")
        options.add_argument("--incognito")

    return options

async def initialize_browser() -> webdriver.Chrome:
    """Initialize and return a Chrome browser instance."""
    options = create_browser_options()
    driver = await webdriver.Chrome(options=options)
    await driver.maximize_window()
    await driver.sleep(1)
    return driver

