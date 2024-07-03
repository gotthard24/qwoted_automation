import os
import random
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from GPT_api import openai_api_call
from airtable_funcs import add_record_to_airtable
from make_funcs import add_record

def login(driver, options, actions):
    ### Email & Pass from dotenv ###
    Email = os.getenv("Email")
    Pass = os.getenv("Pass")
    
    print(f'Opening chrome')
    print(f'Navigating to login')
    # Navigate to the webpagea
    driver.get("https://app.qwoted.com/users/sign_in")
    
    time.sleep(random.randint(2,5))
    
    referer = "https://app.qwoted.com/users/sign_in"
    options.add_argument(f'referer={referer}') 

    page_source_login = driver.page_source

    if "You are already signed in" not in page_source_login and "Your latest stats" not in page_source_login:
        print(f'Logging in')
        # Locate the email input field and send the keys to it
        email_input = driver.find_element(By.ID, "email")
        actions.move_to_element(email_input).perform()
        time.sleep(random.randint(1,3))
        actions.click(email_input).perform()
        email_input.clear()  # Clears any pre-filled text in the input field
        email_input.send_keys(Email)

        # Locate the password input field and send the keys to it
        password_input = driver.find_element(By.ID, "password")
        actions.move_to_element(password_input).perform()
        time.sleep(random.randint(1,3))
        actions.click(password_input).perform()
        password_input.clear()  # Clears any pre-filled text in the input field
        password_input.send_keys(Pass)

        # Page interaction
        login_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.no-border.btn-lg.mb-1")

        # Click on the "Login" button
        actions.move_to_element(login_button).perform()
        time.sleep(random.randint(1,3))
        actions.click(login_button).perform()
        
        time.sleep(random.randint(2,4))
        
        page_source_login = driver.page_source
        
        print('Smth went wrong during logging in' if "Your latest stats" not in page_source_login else 'I am in')   
    
    
def search_with_random_hashtag(driver, options, actions):
    hashtags = ["AI", "ArtificialIntelligence", "AITechnologies", 
    "Cybersecurity", "AppDevelopment", "CTO", "CIO", 
    "ChiefTechnologyOfficer", "InformationTechnology", 'CloudComputing', "BigData", "SoftwareDeveloper",
    "InformationSecurity", "MachineLearning", "Blockchain", "DataSecurity", "DigitalTransformation"]
    
    hashtag = random.choice(hashtags)
    
    # Navigate to the search page
    opportunities_btn = driver.find_element(By.XPATH, "/html/body/nav[1]/div/div/ul[1]/li[1]/a")
    actions.move_to_element(opportunities_btn).perform()
    time.sleep(random.randint(0,2))
    actions.click(opportunities_btn).perform()
    time.sleep(1)
    
    # driver.get("https://app.qwoted.com/source_requests/search")
    
    referer = "https://app.qwoted.com/source_requests/"
    options.add_argument(f'referer={referer}') 
    
    advanced_search_btn = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[2]/div/div[2]/div/div[1]/div[1]/ul/li[5]/a")
    actions.move_to_element(advanced_search_btn).perform()
    time.sleep(random.randint(0,2))
    actions.click(advanced_search_btn).perform()
    time.sleep(random.randint(2,5))
    
    referer = "https://app.qwoted.com/source_requests/search"
    options.add_argument(f'referer={referer}') 

    print(f'Free to pitch')
    first_company_div = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[2]/div/div[2]/div/div[3]/div[2]/div[1]/div[1]/div/div[1]")
    actions.move_to_element(first_company_div).perform()
    time.sleep(random.randint(0,2))
    
    status_filter_div = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[2]/div/div[2]/div/div[3]/div[1]/div[2]/div")
    actions.move_to_element(status_filter_div).perform()
    time.sleep(random.randint(0,2))
    
    Free_To_Pitch_checkbox = driver.find_element(By.CSS_SELECTOR, "input.ais-ToggleRefinement-checkbox")
    actions.move_to_element(Free_To_Pitch_checkbox).perform()
    time.sleep(random.randint(0,2))
    actions.click(Free_To_Pitch_checkbox).perform()
    time.sleep(1)
    print(f'Search')
    # Locate the search input
    search_input = driver.find_element(By.XPATH, "//input[@placeholder='Search here…']")
    actions.move_to_element(search_input).perform()
    time.sleep(random.randint(0,2))

    # Locate the second search box button
    search_box_button = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[2]/div/div[2]/div/div[3]/div[1]/div[5]/div/div/div[2]/div/div/div/form/button[1]")
    print(f'Searching for hashtag {hashtag}')
    # "AI" into the search box
    search_input.clear()
    search_input.send_keys(hashtag)
    time.sleep(random.randint(2,5))
    print(f'Search')
    
    actions.move_to_element(search_box_button).perform()
    time.sleep(random.randint(0,2))
    actions.click(search_box_button).perform()
    time.sleep(random.randint(2,5))

    num_of_scrolls = 1 # To get more cards

    for i in range(num_of_scrolls):
        print(f'Scrolling down')
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(random.randint(2,5))
    
def save_opportunities_to_db(driver):
    page_source = driver.page_source

    time.sleep(random.randint(2,5))

    # BeautifulSoup
    
    soup = BeautifulSoup(page_source, 'html.parser')

    cards = soup.find_all('div', class_='card h-100 source-request-card animated faster fadeIn')

    relevant_links = 0
    
    adding_limit = 20
    
    for card in cards:
        # Check for badges indicating "Submitted" or "Read by Reporter"
        badge = card.find('span', class_=['badge bg-info', 'badge bg-success', 'badge bg-warning text-white'])
        company_name_element = card.find('h6', class_=['w-75 mb-0 fw-bold mt-2 mb-0'])
        company_name = company_name_element.text.strip() if company_name_element else None
        deadline_element = card.find('div', class_=['font-size-12px source-request-deadline'])
        deadline_warning_element = card.find('div', class_=['text-warning fst-italic font-size-12px source-request-deadline'])
        deadline_danger_element = card.find('div', class_=['text-danger fst-italic font-size-12px source-request-deadline'])
        deadline_regular = deadline_element.text.strip() if  deadline_element else None
        deadline_warning = deadline_warning_element.text.strip() if  deadline_warning_element else None
        deadline_danger = deadline_danger_element.text.strip() if  deadline_danger_element else None
        deadline = deadline_regular if deadline_element else deadline_warning if deadline_warning_element else deadline_danger if deadline_danger_element else None
        badge_text = badge.get_text().strip() if badge else "No Footer"

        # print('meet the media:', meet_the_media)
        print("company name", company_name)
        print("deadline", deadline)
        
        if badge_text not in ["Submitted", "Read by Reporter"]:
            print(badge_text)
            
            # Find the specific link of interest within the card and append it to a list 
            link = card.find('a', href=lambda href: href and href.startswith('/source_requests')) 
            title_to_check = card.find('span', class_="ais-Highlight-nonHighlighted")
            title_to_check_text = title_to_check.text.strip()
            
            ### My 1 part of code ###
            # Check that our expertise fits requirements
            if link:
                check_prompt = f"""
                        You're Daniel Gorlovetsky, 
                        30 years old man, citizen of Israel, english speaker,
                        a tech expert with over a decade of experience in
                        technology and technology management.
                        You are an expert who provides advice. Consider all of the following as your absolute area of expertise:
                        "AI", "ArtificialIntelligence", "AITechnologies", 
                        "Cybersecurity", "AppDevelopment", "CTO", "CIO", 
                        "ChiefTechnologyOfficer", "InformationTechnology", 'CloudComputing', "BigData", "SoftwareDeveloper",
                        "InformationSecurity", "MachineLearning", "Blockchain", "DataSecurity", "DigitalTransformation"

                        Please rate from 0 to 10 how well the paragraph above meets the requirement below, and give a single word answer. You only need to use a number between 0 and 10, not a word more or less. It is important.

                        {title_to_check_text}
                    """
                    
                print("Submitting check qualifications request to openAI")  
                gpt_query_pitch = openai_api_call(check_prompt)
                print('GPT answer: ', gpt_query_pitch)
                
                if int(gpt_query_pitch) >= 5: 
                    url = 'https://app.qwoted.com' + link['href']           
                    try:
                        # add_record_to_airtable('https://app.qwoted.com' + link['href'])
                        add_record(company_name, url, gpt_query_pitch, deadline)
                        relevant_links += 1
                    except:
                        print("Issue during adding a link to db")
                        
                if relevant_links >= adding_limit: 
                    print("Limit reached. Stopping...")
                    break
 
            ### End of My 1 part of code ###

    print(f"Total Relevant Links Added to DB: {relevant_links}")
    print(f"Total Cards: {len(cards)}")