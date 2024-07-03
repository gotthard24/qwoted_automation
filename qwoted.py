import time
import random
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from airtable_funcs import get_all_records, update_record_status
from make_funcs import get_records_todo, update_by_rec_id
from dotenv import load_dotenv
from save_funcs import login, search_with_random_hashtag, save_opportunities_to_db
from pitch_funcs import get_query_description, validate_url, find_reporters_name, find_start_pitch_button, find_which_to_pitch_button, fill_pitch_text_area, click_submit, summary_and_quit

load_dotenv()

# Setup Chrome options for AWS Lambda
options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--single-process')
# options.add_argument('--disable-dev-shm-usage')

user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36'
options.add_argument(f'user-agent={user_agent}')

referer = "http://google.com"
options.add_argument(f'referer={referer}')
# # options.binary_location = '/opt/headless-chromium'

# Setup the Chrome driver with the specified options and the path to the binary in the Lambda Layer
driver = webdriver.Chrome(options=options)

#Actions for performing cursor movement like it is a real person
actions = ActionChains(driver)
# Hiding navigator.webdriver
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

def lambda_save_links_handler(event, context):
    login(driver, options, actions)  
    time.sleep(random.randint(1,3))
    search_with_random_hashtag(driver, options, actions)
    time.sleep(random.randint(1,3))
    save_opportunities_to_db(driver)
    
    
def lambda_pitch_handler(event, context):
    total_submitted = 0
    submit_limit = random.randint(4, 7)
    
    login(driver, options, actions)
    
    # Links to validate
    # all_records = get_all_records()

    # records_todo = [{'id': record['id'], **record['fields']} for record in all_records if 'URL' in record['fields'] and record['fields'].get('Status') == 'To do']
    
    todos = get_records_todo()
    
    for record in todos:
        print(f'{record}')
        record_id = record['id']
        url = record['URL']
        fit = record['Fit']
        company_name = record['Name']
        deadline = record['Deadline']
        status = 'In progress'

        driver.get(url)
        
        #Setting previous page 
        referer = url
        options.add_argument(f'referer={referer}')

        is_valid_url = validate_url(driver, url, record_id)
        if is_valid_url == False: continue

        # Getting query description
        query_description = get_query_description(driver)
        print('description: ', query_description)

        # Finding Start to Pitch button
        is_start_pitch_btn_founded = find_start_pitch_button(driver)
        print('I found start pitch button' if is_start_pitch_btn_founded else 'I did not start pitch button')

        time.sleep(random.randint(2,5))
        
        # Getting the reporter's name
        query_reporter_name = find_reporters_name(driver)
        print('reporters name: ',query_reporter_name)
        
        if query_reporter_name == '': continue
        
        # Finding Which to Pitch button
        is_which_to_pitch_btn_founded = find_which_to_pitch_button(driver)
        if is_which_to_pitch_btn_founded == False: continue

        time.sleep(random.randint(2,5))

        # Filling text area with OpenAI api 
        gpt_response = fill_pitch_text_area(driver, query_description, query_reporter_name)

        time.sleep(random.randint(2,5))
        
        # # Finding Submit button
        # is_submit_btn_found = click_submit(driver)
        
        # if is_submit_btn_found: total_submitted += 1
        # else: continue

        # update_record_status(record_id, url, 'In progress')
        update_by_rec_id(record_id, company_name, url, fit, deadline, status, gpt_response)
        
        time.sleep(random.randint(5,10))
        print("Cycle completed successfully")
        
        if total_submitted == submit_limit: 
            break

    response = summary_and_quit(driver, todos, total_submitted)
    # Return the response object
    return response

# lambda_save_links_handler(None, None)
lambda_pitch_handler(None , None)