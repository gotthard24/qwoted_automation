import requests
import json
from dotenv import load_dotenv
import os

load_dotenv()

personal_token = os.getenv("personal_token")

base_id = os.getenv("base_id")

table_name = os.getenv("table_name")

url = f'https://api.airtable.com/v0/{base_id}/{table_name}'

headers = {
    'Authorization': f'Bearer {personal_token}',
    'Content-Type': 'application/json'
}


def add_record_to_airtable(link):
    check_url = f'{url}?filterByFormula={{URL}}="{link}"'
    check_response = requests.get(check_url, headers=headers)

    #Uniqueness check
    if check_response.status_code == 200:
        records = check_response.json().get('records', [])
        if len(records) > 0:
            print('Duplicate URL found. Record not added.')
            return
    else:
        print('Error checking for duplicates:', check_response.status_code)
        print(check_response.json())
        return
    
    #Actual adding
    data = {
        "fields": {
            "URL": link,
        }
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        print('Record added!')
        print(response.json())
    else:
        print('Error:', response.status_code)
        print(response.json())
        
        
def get_all_records():
    url = f'https://api.airtable.com/v0/{base_id}/{table_name}'
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()['records']
    else:
        print(f'Failed to fetch records. Status code: {response.status_code}')
        print(response.json())
        return []
    

def delete_record(record_id):
    url = f'https://api.airtable.com/v0/{base_id}/{table_name}/{record_id}'
    response = requests.delete(url, headers=headers)
    if response.status_code == 200:
        print('Record deleted successfully!')
    else:
        print(f'Failed to delete record. Status code: {response.status_code}')
        print(response.json())
        

def delete_record_by_url(url_to_delete):
    records = get_all_records()
    for record in records:
        fields = record['fields']
        if url_to_delete in fields.values():
            record_id = record['id']
            delete_record(record_id)
            return
    print('No record found with the given cell data.')
    
    
def update_record_status(id, url_data, new_status):
    url = f'https://api.airtable.com/v0/{base_id}/{table_name}/{id}'
    data = {
        'fields': {
            'URL': url_data,
            'Status': new_status
        }
    }
    
    response = requests.put(url, headers=headers, json=data)
    
    if response.status_code == 200:
        print(f"Record with ID {id} updated successfully to '{new_status}'.")
    else:
        print(f"Failed to update record with ID {id}. Status code: {response.status_code}")
        print(response.json())