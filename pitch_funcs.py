from airtable_funcs import delete_record_by_url
from make_funcs import delete_by_rec_id
from GPT_api import openai_api_call
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from bs4 import BeautifulSoup 
import time
import random
import json

def validate_url(driver, url, record_id):
    is_valid = False
    xpath_of_previous_source_request = "//h3[@class='fw-bold my-2' and contains(text(), 'Previous Source Requests')]"
    previous_source_requests_element = driver.find_elements(By.XPATH, xpath_of_previous_source_request)
    
    # Just to simulate Human Behaviour
    time.sleep(random.randint(1, 3))
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(random.randint(1, 3))
    
    if previous_source_requests_element:
        print("Previous source requests found... Continuing to the next one...")
        # delete_record_by_url(url)
        delete_by_rec_id(record_id)

    else:
        print("Previous source requests not found!")
        is_valid = True
    
    return is_valid


def get_query_description(driver):
    div_cssSelector = "div.card-body.py-4.px-5.border-top.position-relative"
    div_element = driver.find_element(By.CSS_SELECTOR, div_cssSelector)

    div_html = div_element.get_attribute('outerHTML')

    soup_for_description = BeautifulSoup(div_html, 'html.parser')

    # Removing ul - First Hashtags
    ul_to_remove = soup_for_description.find('ul', class_='float-start clearfix p-0 m-0')

    if ul_to_remove:
        ul_to_remove.decompose()

    text_without_first_hashtags = soup_for_description.get_text(separator="\n", strip=True)

    # Rmoving all other hashtags - Splitting the text at "Full list..." and keeping the first part
    cleaned_text = text_without_first_hashtags.split("Full list...")[0].strip()

    # Splitting the text into lines
    lines = cleaned_text.split('\n')

    # Skipping the first two lines
    remaining_lines = lines[2:]

    # Joinning the remaining lines back into a single string
    '''query_description for GPT prompt'''
    query_description = '\n'.join(remaining_lines)
    
    return query_description

def find_reporters_name(driver):
    try:
        print("Looking for reporter name element")
        reporter_element = driver.find_element(By.XPATH, "//a[contains(@class, 'fw-bold')]")
        print(f"Reporter name element found. name: {reporter_element.text}")
        query_reporter_name = reporter_element.text
        return query_reporter_name

    except NoSuchElementException:
        print('Reporter name element not found')
        return ''
    
    
def find_start_pitch_button(driver):
    cssSelector_start_a_pitch = "button.btn-primary"
    is_found = False
    try:
        print("Looking for start a pitch element")  
        cssSelector_start_a_pitch_element = driver.find_element(By.CSS_SELECTOR, cssSelector_start_a_pitch)
        driver.execute_script("arguments[0].click();", cssSelector_start_a_pitch_element)
        print("Start a pitch element found")
        is_found = True
    except NoSuchElementException:
        print(f"Failed clicking the start a pitch element. Skipping.")
        
    return is_found

def find_which_to_pitch_button(driver):
    is_found = False
    try:
        print("Looking for who to pitch element")  
        who_to_pitch_name_button = driver.find_element(By.ID, "source_159225")
        print("Who to pitch element found")
        driver.execute_script("arguments[0].click();", who_to_pitch_name_button)
        print("Who to pitch element clicked")
        is_found = True
    except NoSuchElementException:
        print(f"Failed clicking the who to pitch element. Skipping.")
    return is_found


def fill_pitch_text_area(driver, query_description, query_reporter_name):
    prompt = f'''
                    You're Daniel Gorlovetsky, 
                    a tech expert with over a decade of experience in
                    technology and technology management across multiple business verticals. 
                    Your background is in Mobile, frontend, backend development, with touches of DevOps and SecOps. You're a cloud and information security expert.
                    You've founded multiple companies, built, scaled, and took companies public. 
                    You've received a QWOTED query from a journalist who is writing a story. 
                    You're currently the CEO of TLVTech, a technology services powerhouse based in Israel, the startup nation. 
                    Your phone number is +972-50-749-6556 and your email is hi@tlvtech.io. 
                    Write a two-paragraph professional pitch email responding to this query: "{query_description}".
                    The query provided was authored by: "{query_reporter_name}."
                    Sincerely address the author, but not too much, make it without pathos. 
                    Focus the pitch on my expertise in startups, 
                    technology, R&D management, innovation, and leadership and do it concisely, to the point. 
                    Include a persuasive call to action for the reporter to contact me. 
                    Do not leave template parameters and include only the body of the pitch. 
                    No titles, no subjects.
                    '''
    print("Submitting request to openAI")  
    gpt_query_pitch = openai_api_call(prompt)
    print("GPT answer: ", gpt_query_pitch)
        
    pitch_text_form = driver.find_element(By.XPATH, "//*[@id='pitch_text']")
    pitch_text_form.send_keys(gpt_query_pitch)
    return gpt_query_pitch
    
    
def click_submit(driver):
    is_found = False
    try:
        print("Clicking submit")  
        submit_pitch_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.no-border")
        driver.execute_script("arguments[0].click();", submit_pitch_button)
        is_found = True
    except NoSuchElementException:
        print(f"Failed clicking the submit element. Skipping.")
    return is_found


def summary_and_quit(driver, todos, total_submitted):
    print(f"totalRelevantLinks: {len(todos)}")
    print(f"totalSubmitted: {total_submitted}")
    response = {
            "statusCode": 200,
            "body": {
                "message": "Operation completed successfully",
                "totalRelevantLinks": len(todos),
                "total_submitted": total_submitted,
                "linksSample": todos[:5]  # Return up to 5 links as a sample
            }
        }
    # Close the browser
    time.sleep(5)
    driver.quit()

    response["body"] = json.dumps(response["body"])
    return response