from selenium_driverless import webdriver
from selenium_driverless.types.webelement import WebElement
from selenium_driverless.types.by import By
from selenium.common.exceptions import WebDriverException
from utils.helpers import get_proper_string, format_timestamp, extract_experience, scroll_to
from services.db import store_single_job
from config.search import current_experience, good_skills, bad_skills, strict_bad_skills, bad_words
from config.settings import store_in_db

async def process_jobs(driver: webdriver.Chrome, job_listings: list[WebElement], company_name: str, applied: list, rejected: list, count: int, limit: int):
    """
    Process job listings and apply to matching jobs.
    
    Returns:
        tuple: (updated_count, updated_applied, updated_rejected)
    """
    try:
        reason = ""
        for job in job_listings:
            if count >= limit:
                break
                
            position = "Position not found"
            remote_policy = "Remote policy not found"
            compensation = "Compensation not found"
            time = format_timestamp()

            # job object to store
            job_obj = {
                'company_name': company_name,
                'position': position,
                'remote_policy': remote_policy,
                'compensation': compensation,
                'time': time,
                'url': None,
                'type': None,
                'location': None,
                'exp_required': None,
                'application_date': None
            }

            # Check position
            try: 
                position_dom: WebElement = await job.find_element(By.XPATH, './/span[@class="styles_title__xpQDw"]')
                position: str = await position_dom.text
                job_obj['position'] = position

                await driver.sleep(0.5)
            except: 
                reason = f"{position}"
                job_obj['notes'] = reason
                # Store early rejection
                if store_in_db:
                    await store_single_job(job_obj, 'rejected')
                rejected.append(job_obj)
                continue
        
            # Check job location
            try: 
                location_dom: WebElement = await job.find_element(By.XPATH, './/span[@class="styles_locations__HHbZs"]')
                remote_policy = get_proper_string(await location_dom.text)
                job_obj['remote_policy'] = remote_policy
                job_obj['location'] = remote_policy  # Store location as well

                if "in office" in remote_policy.lower():
                    reason = f'{position} is not remote'
                    job_obj['notes'] = reason
                    # Store early rejection
                    if store_in_db:
                        await store_single_job(job_obj, 'rejected')
                    rejected.append(job_obj)
                    continue

                await driver.sleep(0.5)
            except:                     
                reason = f"{remote_policy}"
                job_obj['notes'] = reason
                # Store early rejection
                if store_in_db:
                    await store_single_job(job_obj, 'rejected')
                rejected.append(job_obj)
                continue

            # Check compensation
            try: 
                compensation_dom: WebElement = await job.find_element(By.XPATH, './/span[@class="styles_compensation__3JnvU"]')
                compensation: str = get_proper_string(await compensation_dom.text)
                job_obj['compensation'] = compensation
            except:                     
                reason = f"{compensation}"
                job_obj['notes'] = reason
                # Store early rejection
                if store_in_db:
                    await store_single_job(job_obj, 'rejected')
                rejected.append(job_obj)
                continue
        
            await job.click()
            # wait for job modal to open
            close_button = None
            modal = None
            
            try: 
                modal: WebElement = await driver.find_element(By.XPATH, './/div[contains(@class, "ReactModal__Content")]', timeout=15)
                await driver.sleep(1)
            except: 
                print("Modal not found")
                continue

            try: 
                close_button: WebElement = await driver.find_element(By.XPATH, '//button[@data-test="closeButton"]/*[1]')
                await driver.sleep(1)
            except: 
                print("Modal close button not found")
                continue
            
            try:
                try: 
                    # Try to find the apply button within the modal first, then fallback to driver
                    try:
                        apply_button: WebElement = await modal.find_element(By.XPATH, './/button[@data-test="JobDescriptionSlideIn--SubmitButton"]')
                    except:
                        apply_button: WebElement = await driver.find_element(By.XPATH, '//button[@data-test="JobDescriptionSlideIn--SubmitButton"]')
                    await driver.sleep(1)
                except: 
                    print("Apply button not found")
                    continue

                if await apply_button.get_attribute('disabled'):
                    reason = f"Either already applied or not accepting from location"
                    job_obj['notes'] = reason
                    # Store rejection
                    if store_in_db:
                        await store_single_job(job_obj, 'rejected')
                    rejected.append(job_obj)
                    continue

                try:
                    # Get the wrapper div containing all skills
                    skills: WebElement = await modal.find_element(
                        By.XPATH,
                        './/span[text()="Skills"]/following-sibling::div[contains(@class, "flex")]'
                    )
                except:
                    print("Skills not found")
                    skills = None
                    continue

                if skills:
                    await scroll_to(driver, skills)

                    # Get all individual skill tags inside the wrapper
                    skill_items = await skills.find_elements(By.XPATH, './div')

                    # Extract text
                    skillsTextList = [await s.text for s in skill_items]
                    skillsText = get_proper_string(" ".join(skillsTextList))

                    job_obj['skills'] = skillsText
                    skills_low = skillsText.lower()
                    
                    # Split skills into individual words for comparison
                    skill_words = skills_low.split()
                    
                    # Helper function to check if any word from job skills matches any skill in a list
                    def word_matches_skill(word, skill_list):
                        """Check if a word matches any skill (handles both single and multi-word skills)"""
                        word_lower = word.lower().strip()
                        for skill in skill_list:
                            skill_lower = skill.lower().strip()
                            # Exact match
                            if word_lower == skill_lower:
                                return skill
                            # If skill is multi-word, check if word is part of it
                            if ' ' in skill_lower and word_lower in skill_lower:
                                return skill
                            # If skill is single word and word contains it (for partial matches like "pentesting" contains "testing")
                            if ' ' not in skill_lower and skill_lower in word_lower and len(skill_lower) >= 3:
                                return skill
                        return None
                    
                    # Check each word in job skills against good/bad skills
                    # First check full phrases, then individual words
                    good_word = next((skill for skill in good_skills if skill.lower() in skills_low), False)
                    if not good_word:
                        for word in skill_words:
                            matched_skill = word_matches_skill(word, good_skills)
                            if matched_skill:
                                good_word = matched_skill
                                break
                    
                    if not good_word:
                        # Check full phrases first
                        bad_word = next((skill for skill in bad_skills if skill.lower() in skills_low), False)
                        if not bad_word:
                            # Then check each word
                            for word in skill_words:
                                matched_skill = word_matches_skill(word, bad_skills)
                                if matched_skill:
                                    bad_word = matched_skill
                                    break
                        
                        if bad_word:
                            reason = f'Found bad skill {bad_word}. Skipping.'
                            job_obj['notes'] = reason
                            if store_in_db:
                                await store_single_job(job_obj, 'rejected')
                            rejected.append(job_obj)
                            continue

                    # Check strict bad skills - first as phrases, then individual words
                    strict_bad_word = next((skill for skill in strict_bad_skills if skill.lower() in skills_low), False)
                    if not strict_bad_word:
                        for word in skill_words:
                            matched_skill = word_matches_skill(word, strict_bad_skills)
                            if matched_skill:
                                strict_bad_word = matched_skill
                                break
                    
                    if strict_bad_word:
                        reason = f'Found strict bad skill {strict_bad_word}. Skipping.'
                        job_obj['notes'] = reason
                        if store_in_db:
                            await store_single_job(job_obj, 'rejected')
                        rejected.append(job_obj)
                        continue

                # check for required experience & bad words
                try: description_dom: WebElement = await modal.find_element(By.XPATH, '//div[@id="job-description"]')
                except: 
                    print("Description not found")
                    continue

                await scroll_to(driver, description_dom)

                description = get_proper_string(await description_dom.text)
                job_obj['description'] = description

                desc_low = description.lower()

                # Check experience from job title
                title_exp = extract_experience(position, current_experience)
                
                # Check experience from ul element in modal
                ul_exp = None
                try:
                    ul_element = await modal.find_element(By.XPATH, './/ul[contains(@class, "flex flex-wrap")]', timeout=5)
                    if ul_element:
                        ul_text = await ul_element.text
                        ul_exp = extract_experience(ul_text, current_experience)
                except:
                    pass  # ul element not found, continue

                # Check experience from description
                desc_exp = extract_experience(desc_low, current_experience)

                # Collect all experience requirements found
                exp_requirements = []
                if title_exp:
                    exp_requirements.append(("title", title_exp))
                if ul_exp:
                    exp_requirements.append(("ul", ul_exp))
                if desc_exp:
                    exp_requirements.append(("description", desc_exp))

                # Check if any requirement exceeds current experience
                exp_check_failed = False
                if exp_requirements:
                    # Use the first found requirement for display, but check all
                    source, (lower_limit, upper_limit, exp_text, is_minimum) = exp_requirements[0]
                    job_obj['exp_required'] = exp_text
                    
                    # Check all sources - reject if any requires more experience
                    for source_name, (lower, upper, exp_text_val, is_min) in exp_requirements:
                        # For minimum requirements (e.g., "2 years" = at least 2 years)
                        # Check if current_experience >= lower
                        # For ranges (e.g., "2-5 years"), check if current_experience is within range
                        if is_min:
                            # Minimum requirement: check if current_experience >= lower
                            if current_experience < lower:
                                reason = f"Not enough experience (required: {exp_text_val}, found in {source_name})"
                                job_obj['notes'] = reason
                                # Store rejection
                                if store_in_db:
                                    await store_single_job(job_obj, 'rejected')
                                rejected.append(job_obj)
                                exp_check_failed = True
                                break
                        else:
                            # Range requirement: check if current_experience is within range
                            if not (lower <= current_experience <= upper):
                                reason = f"Not enough experience (required: {exp_text_val}, found in {source_name})"
                                job_obj['notes'] = reason
                                # Store rejection
                                if store_in_db:
                                    await store_single_job(job_obj, 'rejected')
                                rejected.append(job_obj)
                                exp_check_failed = True
                                break
                else:
                    job_obj['exp_required'] = None
                
                if exp_check_failed:
                    continue
                
                skip = False
                for word in bad_words:
                    if word.lower() in desc_low:
                        reason = f"Skipped job due to bad word {word} found in description"
                        job_obj['notes'] = reason
                        # Store rejection
                        if store_in_db:
                            await store_single_job(job_obj, 'rejected')
                        rejected.append(job_obj)
                        skip = True
                        break
                if skip: continue
                
                # Get job URL from current page
                try:
                    job_url = await driver.current_url
                    job_obj['url'] = job_url
                except:
                    job_obj['url'] = None

                # Try to get job type (Full-time, Part-time, etc.)
                try:
                    # Look for job type in the modal
                    type_elements = await modal.find_elements(By.XPATH, './/span[contains(text(), "Full-time") or contains(text(), "Part-time") or contains(text(), "Contract") or contains(text(), "Internship")]')
                    if type_elements:
                        job_obj['type'] = await type_elements[0].text
                    else:
                        job_obj['type'] = None
                except:
                    job_obj['type'] = None

                try: 
                    text_area: WebElement = await modal.find_element(By.XPATH, '//textarea[contains(@id, "form-input")]')
                    await text_area.clear()
                    await text_area.send_keys(f"Hello! I'd like to apply for the {position} role at {company_name}.")
                except: print("Text area not found")

                # Set application date when actually applying
                job_obj['application_date'] = format_timestamp()

                await apply_button.click()
                
                # Store job immediately in database
                if store_in_db:
                    success = await store_single_job(job_obj, 'applied')
                    if success:
                        print(f"✓ Stored applied job: {position} at {company_name}")
                    else:
                        print(f"✗ Failed to store applied job: {position} at {company_name}")
                
                applied.append(job_obj)
                count += 1
            except WebDriverException as e:
                print(e)
                job_obj['notes'] = reason
                
                # Store rejected job immediately in database
                if store_in_db:
                    success = await store_single_job(job_obj, 'rejected')
                    if success:
                        print(f"✓ Stored rejected job: {job_obj.get('position', 'Unknown')} at {company_name} - {reason}")
                    else:
                        print(f"✗ Failed to store rejected job: {job_obj.get('position', 'Unknown')} at {company_name}")
                
                rejected.append(job_obj)
                continue
            finally:
                # Safely close the modal if it's still open
                try:
                    if close_button is not None:
                        try:
                            # Try to check if button is visible (might fail if element is stale)
                            if await close_button.is_visible():
                                await close_button.click()
                                await driver.sleep(1)
                        except Exception:
                            # Element might be stale, try to find it again
                            try:
                                close_button_new = await driver.find_element(By.XPATH, '//button[@data-test="closeButton"]/*[1]', timeout=2)
                                if await close_button_new.is_visible():
                                    await close_button_new.click()
                                    await driver.sleep(1)
                            except Exception:
                                # Modal might already be closed or page changed, ignore
                                pass
                except Exception as e:
                    # Ignore errors when trying to close modal
                    pass
        
        return count
                
    except WebDriverException as e:
        print("error in process_jobs")
        raise e

