# Used midway for fixing an error

import os
import pandas as pd
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()

sf = Salesforce(
    username=os.getenv("SF_USERNAME"), 
    password=os.getenv("SF_PASSWORD"), 
    security_token=os.getenv("SF_SECURITY_TOKEN"), 
    domain=os.getenv("SF_DOMAIN", "login")
)

print("Reading the unsubscribed CSV file...")
df = pd.read_csv("data/clean_UNSUBSCRIBED_import.csv")

# SMART COLUMN DETECTION: Find the column that looks like an email header
email_col = None
for col in df.columns:
    if "email" in str(col).lower().strip():
        email_col = col
        break

if not email_col:
    print("Could not find any column in CSV containing the word 'email'!")
    print(f"Your CSV columns are: {list(df.columns)}")
    exit()

print(f"Found email column named: '{email_col}'")

# Create a clean, lowercase set of all unsubscribed emails using the auto-detected column
unsubscribed_emails = set(str(email).strip().lower() for email in df[email_col].dropna())
print(f"Loaded {len(unsubscribed_emails)} unique emails from your local file.")

print("Querying Salesforce for all contacts imported today...")
query_str = "SELECT Id, Email FROM Contact WHERE CreatedDate = TODAY"
result = sf.query_all(query_str)
sf_records = result.get('records', [])
print(f"Found {len(sf_records)} total contacts in Salesforce created today.")

print("⚡ Matching and updating fields...")
updated_count = 0

for record in sf_records:
    sf_email = str(record.get("Email", "")).strip().lower()
    
    if sf_email in unsubscribed_emails:
        try:
            sf.Contact.update(record['Id'], {
                "EmailOptOut": True
            })
            updated_count += 1
            if updated_count % 100 == 0:
                print(f"Successfully checked {updated_count} boxes...")
        except Exception as e:
            print(f"Failed to update record {record['Id']}: {e}")

print(f" Successfully forced the 'Email Opt Out' checkbox to True for {updated_count} contacts.")