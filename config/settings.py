headless = False

# Chrome executable path (leave as None to auto-detect, or specify full path like r"C:\Program Files\Google\Chrome\Application\chrome.exe")
chrome_path = None

store_in_db = True

send_email = False

hide_companies = False

# Number of jobs to apply to
limit = 5

# Location type filter: List of allowed location types
# Options: "remote", "in office", "hybrid"
# Examples:
#   ["remote"] - Only remote jobs
#   ["remote", "hybrid"] - Remote and hybrid jobs (not in-office)
#   [] - Accept all location types (no filter)
location_type = ["remote"]