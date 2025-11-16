from selenium_driverless import webdriver
from selenium_driverless.types.by import By
from selenium_driverless.types.webelement import WebElement
from selenium.common.exceptions import ElementNotVisibleException, WebDriverException, NoSuchElementException
from datetime import datetime
import re

def get_proper_string(value: str) -> str: 
    """Returns a string stripped and which maintains its idents and breaks"""
    return '\n'.join([' '.join(line.split()) for line in value.splitlines()]).strip()

async def wait_for_disappearance(driver: webdriver.Chrome, element: WebElement, timeout=3): 
    """Wait till the element is no longer displayed"""
    if await element.is_visible():
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

def format_timestamp():
    # Format timestamp as dd-mm-yy:hh:mm:ss
    return datetime.now().strftime(f"%d-%m-%y:%H:%M:%S")

def extract_experience(text: str, current_experience: int = 100):
    """Extract experience requirement from text. Returns (lower_limit, upper_limit, exp_text, is_minimum) or None
    is_minimum: True if it's a minimum requirement (e.g., "2 years"), False if it's a range (e.g., "2-5 years")
    """
    if not text:
        return None
    text_lower = text.lower()
    
    # Check for "No experience required" or similar phrases
    no_exp_patterns = [
        r'no\s+experience',
        r'no\s+exp',
        r'experience\s+not\s+required',
        r'entry\s+level',
        r'fresh\s+graduate',
        r'fresher'
    ]
    for pattern in no_exp_patterns:
        if re.search(pattern, text_lower):
            return (0, 100, "No experience required", False)
    
    # Pattern to match: "6 years", "6 years of exp", "3-5 years", "5+ years", etc.
    # Matches: year, years, yr, yrs (both singular and plural forms)
    # Try pattern for "X years of exp" or "X years" first (means at least X years - MINIMUM requirement)
    simple_pattern = re.compile(r'(\d+)\s*(?:year|years|yr|yrs)(?:\s+of\s+exp)?', re.IGNORECASE)
    simple_match = simple_pattern.search(text_lower)
    if simple_match:
        years = int(simple_match.group(1))
        # For "X years", this is a MINIMUM requirement (at least X years)
        # Use upper_limit = -1 as sentinel to indicate "minimum only"
        return (years, -1, f"{years}+ years", True)
    
    # Try pattern for ranges: "3-5 years", "3 to 5 years", etc.
    range_pattern = re.compile(r'(\d+)\s*[-to]+\s*(\d+)\s*(?:year|years|yr|yrs)(?:\s+of\s+exp)?', re.IGNORECASE)
    range_match = range_pattern.search(text_lower)
    if range_match:
        lower = int(range_match.group(1))
        upper = int(range_match.group(2))
        return (lower, upper, f"{lower}-{upper} years", False)
    
    # Try pattern with parentheses: "(3) years" or "3+ years"
    complex_pattern = re.compile(r'(?:\(\s*(\d+)\s*\)|(\d+))?\s*[-to]*\s*(\d+)?\+?\s*(?:year|years|yr|yrs)(?:\s+of\s+exp)?', re.IGNORECASE)
    complex_match = complex_pattern.search(text_lower)
    if complex_match:
        lower_limit = int(complex_match.group(1) or complex_match.group(2) or 0)
        if complex_match.group(3):
            # It's a range
            upper_limit = int(complex_match.group(3))
            exp_text = f"{lower_limit}-{upper_limit} years"
            return (lower_limit, upper_limit, exp_text, False)
        else:
            # It's a minimum requirement (has + or just a number)
            exp_text = f"{lower_limit}+ years"
            return (lower_limit, -1, exp_text, True)
    
    return None

