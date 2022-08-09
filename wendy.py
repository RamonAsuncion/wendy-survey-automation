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

# Used for the implicitly_wait function. Delay the time of responses.
DELAY_TIME = 1

# ID's for specific question.
GENDER_ID = "R000037"
AGE_ID = "R000038"
HOUSE_HOLD_INCOME_ID = "R000039"

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
    print("Using FAKE user agent: " + "\n" + user_agent)
    options.add_argument("user-agent=" + user_agent)
        
    # Locate the path to the chrome driver and run it.
    chrome_service = ChromeService(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=chrome_service, options=options)
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
        xpath_expression = ""

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

        # Select the best option on the table questions (highly satifised).
        xpath_expression = '//td[@class="HighlySatisfiedNeitherDESCQuestion" or "HighlyLikelyDESCQuestion"]' 

        # Check if the highly satisfied table exist.
        best_option_table = driver.find_elements(By.XPATH, xpath_expression)
      
        # Options that need specific answers.
        if experience:
            multiple_choice[1].click() 
        elif employee:
            employee[0].click()
        elif dine_in:
            dine_in[0].click() 
        elif text_area:
            try:
                text_area = text_area[0] 
                text_area.send_keys(Keys.TAB)
                text_area.clear()
                text_area.send_keys(r.choice(list(open('good_comments.txt'))))
            except FileNotFoundError:
                print("[ERROR] File not found. Skipping writing a comment.") 
        elif yes_no_table:
            xpath_expression = "//td[@class='Opt1 inputtyperbloption']//span[@class='radioSimpleInput']" 
            best_option = driver.find_elements(By.XPATH, xpath_expression)
            for i in range(len(best_option)):
                best_option[i].click() 
        elif best_option_table:
            # If the highly satisfied table exist, choose the best option.
            xpath_expression = "//td[@class='Opt5 inputtyperbloption']//span[@class='radioSimpleInput']" 
            best_option = driver.find_elements(By.XPATH, xpath_expression)
            for i in range(len(best_option)):
                best_option[i].click()
        else:
            # If does not meet any creteria above choose a random option.
            multiple_choice[r.randint(0, len(multiple_choice))-1].click()
                        
        # Click the next button.
        next_button = driver.find_elements(By.ID, "NextButton")

        # Reached the end page where you choose question.
        fill_out_data = driver.find_elements(By.ID, "FNSBlock1200")
        if len(fill_out_data) > 0:
            break

        # Proceed to the next page. 
        next_button[0].click()
        
    # Select a randomized attributes of a person.
    randomize_person_option()

    # No employee went above and beyond.
    multiple_choice = driver.find_elements(By.CLASS_NAME, "radioSimpleInput")
    multiple_choice[1].click()
    driver.find_element(By.ID, "NextButton").click()
    
    # I don't want no cash rewards.
    multiple_choice = driver.find_elements(By.CLASS_NAME, "radioSimpleInput")
    multiple_choice[1].click()
    driver.find_element(By.ID, "NextButton").click()
        
        
def randomize_person_option():
    print("Randomizing person options...")
    
    # Randomize the person's gender.
    Select(driver.find_element(By.ID, GENDER_ID)).select_by_value(str(r.randint(1,2)))   
    
    # Randomize the person's age.
    Select(driver.find_element(By.ID, AGE_ID)).select_by_value(str(r.randint(2,6))) 
    
    # Randomize the person's house hold income.
    Select(driver.find_element(By.ID, HOUSE_HOLD_INCOME_ID)).select_by_value(str(r.randint(1,6))) 
        
    
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
    
    