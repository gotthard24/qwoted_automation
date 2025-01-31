import requests

def get_records_todo():
    webhook_url = 'https://hook.eu1.make.com/8elo632g1i9w3mpandntzwydsxux73vb'

    response = requests.get(webhook_url)

    if response.status_code == 200:
        data = response.json() 
        return data
    else:
        print(f"Error: {response.status_code}")
        

def add_record(name, url, fit, deadline):
    webhook_url = 'https://hook.eu1.make.com/8elo632g1i9w3mpandntzwydsxux73vb'
    data = {"name": name,
            "url": url,
            "fit": fit,
            "deadline": deadline}

    response = requests.post(webhook_url, json=data)

    if response.status_code == 200:
        print("Record added successfully or already exist in db!")
    else:
        print(f"Error: {response.status_code}")
        
        
def delete_by_rec_id(rec_id):
    webhook_url = 'https://hook.eu1.make.com/8elo632g1i9w3mpandntzwydsxux73vb'
    data = {"record_id": rec_id}

    response = requests.post(webhook_url, json=data)

    if response.status_code == 200:
        print("Record successfully deleted!")
    else:
        print(f"Error: {response.status_code}")
        

def update_by_rec_id(rec_id, name, url, fit, deadline, status, gpt_response):
    webhook_url = 'https://hook.eu1.make.com/8elo632g1i9w3mpandntzwydsxux73vb'
    data = {"record_id": rec_id,
            "name": name,
            "url": url,
            "fit": fit,
            "deadline": deadline,
            "status": status,
            "response": gpt_response}

    response = requests.post(webhook_url, json=data)

    if response.status_code == 200:
        print("Record successfully updated!")
    else:
        print(f"Error: {response.status_code}")