import os
from dotenv import load_dotenv 
from flask import Flask, request, jsonify, make_response
from simple_salesforce import Salesforce 

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# 2. Login to Salesforce using .env values
try:
    sf = Salesforce(
        username=os.getenv('SF_USERNAME'),
        password=os.getenv('SF_PASSWORD'),
        security_token=os.getenv('SF_SECURITY_TOKEN') 
    )
    print("Connected to Salesforce successfully")
except Exception as e:
    print(f"SF Connection Failed: {e}")

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # If Eventbrite or a browser pings with a GET request
    if request.method == 'GET':
        print("Verification ping received")
        response = make_response("Webhook active and ready", 200)
        response.headers["ngrok-skip-browser-warning"] = "true"
        return response

    # If Eventbrite sends the actual order POST data
    data = request.json
    print("Eventbrite Webhook Received")
    print(data)
    
    # 3. Handle data parsing & Salesforce Lead insertion here
    try:
        # Example: Lead record in Salesforce
        new_lead = sf.Lead.create({
            'FirstName': 'Test',
            'LastName': 'EventbriteAttendee',
            'Company': 'Eventbrite Registration',
            'Email': 'test@example.com'
        })
        print(f"Lead created successfully in Salesforce! ID: {new_lead['id']}")
    except Exception as e:
        print(f"Failed to push to Salesforce: {e}")
    
    response = make_response(jsonify({"status": "success"}), 200)
    response.headers["ngrok-skip-browser-warning"] = "true"
    return response

if __name__ == '__main__':
    app.run(port=8000, debug=True)