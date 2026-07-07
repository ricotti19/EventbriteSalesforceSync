import os
import time
import pandas as pd
from dotenv import load_dotenv
from simple_salesforce import Salesforce, SalesforceMalformedRequest

load_dotenv()

USERNAME = os.getenv("SF_USERNAME")
PASSWORD = os.getenv("SF_PASSWORD")
SECURITY_TOKEN = os.getenv("SF_SECURITY_TOKEN")
DOMAIN = os.getenv("SF_DOMAIN", "login") # 'test' for sandbox, 'login' for production

def run_upload():
    print("Connecting to Salesforce...")
    try:
        # simple-salesforce handles authentication, token generation, and base URLs
        sf = Salesforce(
            username=USERNAME, 
            password=PASSWORD, 
            security_token=SECURITY_TOKEN, 
            domain=DOMAIN
        )
        print("Authenticated successfully!")
    except Exception as e:
        print(f"Authentication failed: {e}")
        return

    print("Loading clean CSV data...")
    df = pd.read_csv("data/clean_SUBSCRIBED_import.csv")

    print(f"Processing {len(df)} contacts for Salesforce upload...")

    # Format the dataframe columns straight into a list of dictionaries that Salesforce expects
    records = []
    for _, row in df.iterrows():
        # Salesforce field names are case-sensitive standard API names
        contact = {
            "FirstName": str(row.get("First Name", "")).strip(),
            "LastName": str(row.get("Last Name", "")).strip(),
            "Email": str(row.get("Email", "")).strip(),
        }
        
        # Salesforce requires a LastName. If empty, give placeholder or skip
        if not contact["LastName"] or contact["LastName"] == "nan":
            contact["LastName"] = "Unknown"
            
        records.append(contact)

    # Chunk records into batches of 100 for stability
    batch_size = 100
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        print(f"Sending batch {i // batch_size + 1} ({len(batch)} records)...")
        
        try:
            # The Composite API inserts multiple records in a single API call
            results = sf.bulk.Contact.insert(batch, batch_size=batch_size)
            
            # Check for individual record errors inside the batch responses
            success_count = sum(1 for res in results if res.get('success'))
            print(f" Successfully inserted {success_count}/{len(batch)} records.")
            
        except SalesforceMalformedRequest as json_err:
            print(f" Payload format error: {json_err}")
        except Exception as e:
            print(f" Batch error occurred: {e}")
            
        time.sleep(0.5) # Gentle rate-limit buffer

    print("Salesforce Upload Complete!")

if __name__ == "__main__":
    run_upload()