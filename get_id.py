import os
import requests # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()
TOKEN = os.getenv('EVENTBRITE_TOKEN')

if not TOKEN:
    print("Error: EVENTBRITE_TOKEN not found in your .env file!")
    exit()

url = "https://www.eventbriteapi.com/v3/users/me/organizations/"
headers = {"Authorization": f"Bearer {TOKEN}"}

try:
    res = requests.get(url, headers=headers).json()
    orgs = res.get('organizations', [])
    if orgs:
        print("\n🎉 Found your Organization ID!")
        for o in orgs:
            print(f"Name: {o.get('name')} | ID: {o.get('id')}")
    else:
        print("Connected to Eventbrite, but found 0 organizations linked to this token.")
except Exception as e:
    print(f"Error fetching data: {e}")