from openai import OpenAI
from dotenv import load_dotenv
import os

def openai_api_call(prompt):

    load_dotenv()

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    client = OpenAI(
        api_key = OPENAI_API_KEY
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"{prompt}",
            }
        ],
        model="gpt-3.5-turbo",
    )

    response_content = chat_completion.choices[0].message.content
    
    return(response_content)