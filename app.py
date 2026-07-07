import os
from dotenv import load_dotenv 
from flask import Flask, request, jsonify, make_response
from simple_salesforce import Salesforce 

# Load environment variables from .env file (for local testing)
load_dotenv()

app = Flask(__name__)

def get_salesforce_client():
    """Initializes Salesforce client dynamically using environment variables."""
    try:
        return Salesforce(
            username=os.getenv('SF_USERNAME'),
            password=os.getenv('SF_PASSWORD'),
            security_token=os.getenv('SF_SECURITY_TOKEN') 
        )
    except Exception as e:
        print(f"❌ SF Connection Failed: {e}")
        return None

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    # 1. Handle Eventbrite or browser verification pings (GET)
    if request.method == 'GET':
        print("🔍 GET Verification ping received")
        response = make_response("Webhook active and ready", 200)
        return response

    # 2. Safely capture incoming POST data
    try:
        data = request.get_json(silent=True)
    except Exception:
        data = None

    # 3. If Eventbrite sends an empty POST request just to test the connection, 
    # respond with a 200 OK immediately so it saves successfully.
    if not data:
        print("ℹ️ Empty test ping received from Eventbrite. Verifying connection.")
        return make_response(jsonify({"status": "verified"}), 200)

    print("📥 Actual Eventbrite Webhook Data Received:")
    print(data)
    
    # 4. Connect to Salesforce dynamically
    sf = get_salesforce_client()
    if not sf:
        print("❌ Aborting Salesforce push: Client not initialized.")
        return make_response(jsonify({"status": "error", "message": "Salesforce connection failed"}), 500)

    # 5. Handle data parsing & Salesforce Lead insertion
    try:
        # Example: Lead record in Salesforce
        new_lead = sf.Lead.create({
            'FirstName': 'Test',
            'LastName': 'EventbriteAttendee',
            'Company': 'Eventbrite Registration',
            'Email': 'test@example.com'
        })
        print(f"✅ Lead created successfully in Salesforce! ID: {new_lead['id']}")
    except Exception as e:
        print(f"❌ Failed to push to Salesforce: {e}")
    
    response = make_response(jsonify({"status": "success"}), 200)
    return response

if __name__ == '__main__':
    # Render binds to port 10000 by default, fallback to 8000 locally
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=True)