import os
import requests
from dotenv import load_dotenv 
from flask import Flask, request, jsonify, make_response
from simple_salesforce import Salesforce 

load_dotenv()

app = Flask(__name__)

EVENTBRITE_TOKEN = os.getenv('EVENTBRITE_PRIVATE_TOKEN') 

def get_salesforce_client():
    try:
        return Salesforce(
            username=os.getenv('SF_USERNAME'),
            password=os.getenv('SF_PASSWORD'),
            security_token=os.getenv('SF_SECURITY_TOKEN') 
        )
    except Exception as e:
        print(f"SF Connection Failed: {e}")
        return None

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        print("GET Verification ping received")
        response = make_response("Webhook active and ready", 200)
        return response

    try:
        data = request.get_json(silent=True)
    except Exception:
        data = None

    if not data:
        print("Empty test ping received from Eventbrite. Verifying connection.")
        return make_response(jsonify({"status": "verified"}), 200)

    print("Actual Eventbrite Webhook Data Received:")
    print(data)
    
    api_url = data.get('api_url')
    if not api_url:
        return make_response(jsonify({"status": "ignored"}), 200)

    first_name = "Eventbrite"
    last_name = "Attendee"
    email = "no-email@example.com"

    try:
        headers = {"Authorization": f"Bearer {EVENTBRITE_TOKEN}"}
        response = requests.get(f"{api_url}?expand=attendees", headers=headers)
        if response.status_code == 200:
            order_info = response.json()
            attendees = order_info.get('attendees', [])
            if attendees:
                profile = attendees[0].get('profile', {})
                first_name = profile.get('first_name', 'Eventbrite')
                last_name = profile.get('last_name', 'Attendee')
                email = profile.get('email', 'no-email@example.com')
                print(f"Extracted: {first_name} {last_name} ({email})")
    except Exception as e:
        print(f"Error communicating with Eventbrite API: {e}")

    sf = get_salesforce_client()
    if not sf:
        print("Aborting Salesforce push: Client not initialized.")
        return make_response(jsonify({"status": "error", "message": "Salesforce connection failed"}), 500)

    try:
        new_lead = sf.Lead.create({
            'FirstName': first_name,
            'LastName': last_name,
            'Company': 'Eventbrite Registration',
            'Email': email
        })
        print(f"Lead created successfully in Salesforce! ID: {new_lead['id']}")
    except Exception as e:
        print(f"Failed to push to Salesforce: {e}")
    
    response = make_response(jsonify({"status": "success"}), 200)
    return response

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)