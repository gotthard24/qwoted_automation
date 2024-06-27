import time
import random
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from airtable_funcs import get_all_records, update_record_status
from dotenv import load_dotenv
from save_funcs import login, search_with_random_hashtag, save_opportunities_to_db
from pitch_funcs import get_query_description, validate_url, find_reporters_name, find_start_pitch_button, find_which_to_pitch_button, fill_pitch_text_area, click_submit

load_dotenv()

# Setup Chrome options for AWS Lambda
options = Options()
# options.add_argument('--headless')
# options.add_argument('--no-sandbox')
# options.add_argument('--single-process')
# options.add_argument('--disable-dev-shm-usage')
# # options.binary_location = '/opt/headless-chromium'

# Setup the Chrome driver with the specified options and the path to the binary in the Lambda Layer
driver = webdriver.Chrome(options=options)

def lambda_save_links_handler(event, context):
    login(driver)
    time.sleep(random.randint(1,3))
    search_with_random_hashtag(driver)
    time.sleep(random.randint(1,3))
    save_opportunities_to_db(driver)
    
    
def lambda_pitch_handler(event, context):
    total_submitted = 0
    submit_limit = random.randint(4, 7)
    login(driver)
    
    # Links to validate
    all_records = get_all_records()

    records_todo = [{'id': record['id'], **record['fields']} for record in all_records if 'URL' in record['fields'] and record['fields'].get('Status') == 'To do']

    for record in records_todo:
        print(f'{record}')
        record_id = record['id']
        url = record['URL']

        driver.get(url)
        
        is_valid_url = validate_url(driver, url)
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
        fill_pitch_text_area(driver, query_description, query_reporter_name)

        time.sleep(random.randint(2,5))
        
        # # Finding Submit button
        # is_submit_btn_found = click_submit(driver)
        # if not is_submit_btn_found: total_submitted += 1
        # else: continue

        update_record_status(record_id, url, 'In progress')
        
        time.sleep(random.randint(5,10))
        print("Cycle completed successfully")
        
        if total_submitted == submit_limit: 
            break

    print(f"totalRelevantLinks: {len(records_todo)}")
    print(f"totalSubmitted: {total_submitted}")
    response = {
            "statusCode": 200,
            "body": {
                "message": "Operation completed successfully",
                "totalRelevantLinks": len(records_todo),
                "total_submitted": total_submitted,
                "linksSample": records_todo[:5]  # Return up to 5 links as a sample
            }
        }
    # Close the browser
    time.sleep(5)
    driver.quit()
    import json
    response["body"] = json.dumps(response["body"])

    # Return the response object
    return response

# lambda_save_links_handler(None, None)
lambda_pitch_handler(None , None)