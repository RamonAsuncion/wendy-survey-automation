# Python modules.
import random as r
from datetime import date
import os

# Selenium modules.
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.keys import Keys

# Error handling.
from selenium.common.exceptions import WebDriverException

# Fake agent module
from fake_useragent import UserAgent

# Load in .env file with secret restaurant.
from dotenv import load_dotenv
load_dotenv('.env') 

# Constants for the survey.
SURVEY_WEBSITE = 'https://wendyswantstoknow.com/'
CHROME_DRIVER_PATH = '/opt/homebrew/bin/chromedriver' 
RESTAURANT_NUMBER = os.environ.get("WENDY_CODE")

# Date and time constants.
MAX_MINUTE_TIME = 59
MIN_MINUTE_TIME = 0
MAX_HOUR_TIME = 12
MIN_HOUR_TIME = 7

# Delay the time of responses in seconds.
DELAY_TIME = 1

def setup_selenium():
    global driver
    
    print("Loading up Selenium...")    
        
    # Options for google chrome.
    options = webdriver.ChromeOptions()
    options.add_argument("window-size=1000,750") # The window size of the Chrome Browser.
    options.add_experimental_option('excludeSwitches', ['enable-logging'])
    
    # Generate a random user agent.
    ua = UserAgent(verify_ssl=False)
    user_agent = ua.random
    print(f"User agent: {user_agent}")
    options.add_argument(f"user-agent={user_agent}")
        
    # Locate the path to the chrome driver and run it.
    chrome_service = ChromeService(executable_path=CHROME_DRIVER_PATH)

    try: 
        # Get the chrome binary to run the chrome driver.
        driver = webdriver.Chrome(service=chrome_service, options=options)
    except WebDriverException:
        print("Error: Cannot find Chrome binary.")
        print("Exiting program.")
        exit(1)

    print("Selenium loaded.")
    
    # Get the survey page.
    driver.get(SURVEY_WEBSITE)
    print("Survey page loaded.")
    
    # Wait for the content of the page to load.
    driver.implicitly_wait(DELAY_TIME)
    

def information_from_receipt():    
    print("Filling out receipt information...")

    # Put the restaurant number in the text box.    
    driver.find_element(By.ID, 'InputStoreNum').send_keys(RESTAURANT_NUMBER)  
    
    # Generate a date for the survey that's between the first day of current month and present day. 
    random_date = str(date.today().month) + "/" + str(r.randint(1, date.today().day-1)) + "/" + str(date.today().year)
    driver.execute_script("document.getElementsByClassName('datePickerBox')[0].removeAttribute('readonly')")    
    driver.find_element(By.ID, 'Index_VisitDateDatePicker').send_keys(random_date)
        
    # Choose a random visiting hour in the morning.
    driver.find_element(By.ID, 'InputHour').send_keys(str(r.randint(MIN_HOUR_TIME, MAX_HOUR_TIME)).zfill(2))   
    driver.find_element(By.ID, 'InputMinute').send_keys(str(r.randint(MIN_MINUTE_TIME, MAX_MINUTE_TIME)).zfill(2))
    driver.find_element(By.ID, 'InputMeridian').send_keys('AM') 
    
    # Complete the introduction.
    driver.find_element(By.ID, "NextButton").click()

def fill_out_survey():
    print("Filling out survey...")
    
    # Confirm that the store is correct. 
    driver.find_elements(By.CLASS_NAME, "radioSimpleInput")[0].click()
    next_button = driver.find_element(By.ID, "NextButton") 
    next_button.click()
    
    next_button = driver.find_elements(By.ID, "NextButton")

    while len(next_button) > 0: 
        # Select the multiple choice questions.
        multiple_choice = driver.find_elements(By.CLASS_NAME, "radioSimpleInput")

        # Question: Did you have a bad experience?
        experience = driver.find_elements(By.ID, "textR000017")
        
        # Choice where you placed an order with an employee.
        employee = driver.find_elements(By.XPATH, "//label[@for='R000108.1']")
        
        # Choice where you ordered your food through dine in.
        dine_in = driver.find_elements(By.XPATH, "//label[@for='R000006.1']")
        
        # Select text box to write a good generic comment.
        text_area = driver.find_elements(By.ID, "S000024")

        # Question that ask the customer yes or no questions.
        yes_no_table = driver.find_elements(By.CLASS_NAME, "YesNoASCQuestion")

        # Select the best option on the table questions (highly satisfied).
        xpath_expression = '//td[@class="HighlySatisfiedNeitherDESCQuestion" or "HighlyLikelyDESCQuestion"]' 

        # Check if the highly satisfied table exist.
        best_option_table = driver.find_elements(By.XPATH, xpath_expression)
        
        # Did a staff member go above and beyond?
        above_and_beyond_question = driver.find_elements(By.ID, "FNSR000041")
        
        # Respond to the conditions.
        if experience:
            handle_experience_question(multiple_choice)
        elif employee:
            handle_employee_question(employee)
        elif dine_in:
            handle_dine_in_question(dine_in)
        elif text_area:
            handle_text_area_question(text_area)
        elif above_and_beyond_question:
            handle_above_and_beyond_question()
            break 
        elif yes_no_table:
            handle_yes_no_table_question()
        elif best_option_table:
            handle_best_option_table_question()
        else:
            # If does not meet any criteria above choose a random option.
            multiple_choice[r.randint(0, len(multiple_choice))-1].click()
                        
        # Click the next button.
        next_button = driver.find_elements(By.ID, "NextButton")

        # Proceed to the next page. 
        next_button[0].click()

# Helper functions 
def handle_experience_question(multiple_choice):
    multiple_choice[1].click()

def handle_employee_question(employee):
    employee[0].click()

def handle_dine_in_question(dine_in):
    dine_in[0].click()

def handle_above_and_beyond_question():
    # No employee went above and beyond.
    multiple_choice = driver.find_elements(By.CLASS_NAME, "radioSimpleInput")
    multiple_choice[1].click()
    driver.find_element(By.ID, "NextButton").click()
    
    # I don't want no cash rewards.
    multiple_choice = driver.find_elements(By.CLASS_NAME, "radioSimpleInput")
    multiple_choice[1].click()
    driver.find_element(By.ID, "NextButton").click()

def handle_text_area_question(text_area):
    if os.path.isfile("good_comments.txt"):
        text_area = text_area[0]
        text_area.send_keys(Keys.TAB)
        text_area.clear()
        text_area.send_keys(r.choice(list(open("good_comments.txt"))))
    else:
        print("[ERROR] File not found. Skipping writing a comment.")

def handle_yes_no_table_question():
    xpath_expression = "//td[@class='Opt1 inputtyperbloption']//span[@class='radioSimpleInput']"
    best_option = driver.find_elements(By.XPATH, xpath_expression)
    for i in range(len(best_option)):
        best_option[i].click()

def handle_best_option_table_question():
    xpath_expression = "//td[@class='Opt5 inputtyperbloption']//span[@class='radioSimpleInput']"
    best_option = driver.find_elements(By.XPATH, xpath_expression)
    for i in range(len(best_option)):
        best_option[i].click()
    
def save_validation_code(): 
    print("Saving validation code...")
    # Save the validation code at the end.
    valid_code = driver.find_elements(By.CLASS_NAME, "ValCode")[0] 
    with open('validation_code.txt', 'a') as f:
        f.write(str(valid_code.get_attribute("textContent")) + "\n")

def main():
    setup_selenium()
    information_from_receipt()
    fill_out_survey()
    save_validation_code()
    print("Done.") 
    driver.quit()

if __name__ == '__main__':
    main()
    