import os
import time
import pandas as pd
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()

USERNAME = os.getenv("SF_USERNAME")
PASSWORD = os.getenv("SF_PASSWORD")
SECURITY_TOKEN = os.getenv("SF_SECURITY_TOKEN")
DOMAIN = os.getenv("SF_DOMAIN", "login") 

def run_bulk_upsert():
    print("🔌Connecting to Salesforce...")
    sf = Salesforce(username=USERNAME, password=PASSWORD, security_token=SECURITY_TOKEN, domain=DOMAIN)
    print("Authenticated successfully!")

    print("Loading single-column CSV data...")
    df = pd.read_csv("data/clean_UNSUBSCRIBED_import.csv")
    
    records = []
    for _, row in df.iterrows():
        email = str(row.get("Email address", "")).strip()
        if email and email != "nan":
            records.append({
                "Email": email,
                "LastName": "Unknown",
                "HasOptedOutOfEmail": True
            })
    
    batch_size = 200
    for i in range(0, len(records), batch_size):
        batch = records[i:i + batch_size]
        try:
            # upsert on the 'Email' field
            results = sf.bulk.Contact.upsert(batch, external_id_field="Email", batch_size=batch_size)
            success_count = sum(1 for res in results if res.get('success'))
            print(f" Successfully processed {success_count}/{len(batch)} records.")
        except Exception as e:
            print(f" Batch error: {e}")
        time.sleep(0.5)

if __name__ == "__main__":
    run_bulk_upsert()