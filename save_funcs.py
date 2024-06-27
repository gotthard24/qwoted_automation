import os
import random
import time
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from GPT_api import openai_api_call
from airtable_funcs import add_record_to_airtable

def login(driver):
    ### Email & Pass from dotenv ###
    Email = os.getenv("Email")
    Pass = os.getenv("Pass")
    
    print(f'Opening chrome')
    print(f'Navigating to login')
    # Navigate to the webpagea
    driver.get("https://app.qwoted.com/users/sign_in")

    page_source_login = driver.page_source

    if "You are already signed in" not in page_source_login and "Your latest stats" not in page_source_login:
        print(f'Logging in')
        # Locate the email input field and send the keys to it
        email_input = driver.find_element(By.ID, "email")
        email_input.clear()  # Clears any pre-filled text in the input field
        email_input.send_keys(Email)

        # Locate the password input field and send the keys to it
        password_input = driver.find_element(By.ID, "password")
        password_input.clear()  # Clears any pre-filled text in the input field
        password_input.send_keys(Pass)

        # Page interaction
        login_button = driver.find_element(By.CSS_SELECTOR, "button.btn.btn-primary.no-border.btn-lg.mb-1")

        # Click on the "Login" button
        login_button.click()
        
        time.sleep(3)
        
        page_source_login = driver.page_source
        
        print('Smth went wrong during logging in' if "Your latest stats" not in page_source_login else 'I am in')    
    
    
def search_with_random_hashtag(driver):
    hashtags = ["AI", "ArtificialIntelligence", "AITechnologies", 
    "Cybersecurity", "AppDevelopment", "CTO", "CIO", 
    "ChiefTechnologyOfficer", "InformationTechnology", 'CloudComputing', "BigData", "SoftwareDeveloper",
    "InformationSecurity", "MachineLearning", "Blockchain", "DataSecurity", "DigitalTransformation"]
    
    hashtag = random.choice(hashtags)

    
    # Navigate to the search page
    driver.get("https://app.qwoted.com/source_requests/search")

    time.sleep(5)

    print(f'Free to pitch')
    Free_To_Pitch_checkbox = driver.find_element(By.CSS_SELECTOR, "input.ais-ToggleRefinement-checkbox")
    Free_To_Pitch_checkbox.click()
    print(f'Search')
    # Locate the search input
    search_input = driver.find_element(By.XPATH, "//input[@placeholder='Search here…']")

    # Locate the second search box button
    search_box_button = driver.find_element(By.XPATH, "/html/body/div[3]/div/div/div[2]/div/div[2]/div/div[3]/div[1]/div[5]/div/div/div[2]/div/div/div/form/button[1]")
    print(f'Searching for hashtag {hashtag}')
    # "AI" into the search box
    search_input.clear()
    search_input.send_keys(hashtag)
    time.sleep(random.randint(2,5))
    print(f'Search')
    search_box_button.click()
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
        meet_the_media = card.find('i', class_=['fas fa-message'])
        badge_text = badge.get_text().strip() if badge else "No Footer"

        print(meet_the_media)
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
                    try:
                        add_record_to_airtable('https://app.qwoted.com' + link['href'])
                        relevant_links += 1
                    except:
                        print("Issue during adding a link to db")
                        
                if relevant_links >= adding_limit: 
                    print("Limit reached. Stopping...")
                    break
 
            ### End of My 1 part of code ###

    print(f"Total Relevant Links Added to DB: {relevant_links}")
    print(f"Total Cards: {len(cards)}")