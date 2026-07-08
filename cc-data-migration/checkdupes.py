# testing
import os
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()

sf = Salesforce(
    username=os.getenv("SF_USERNAME"), 
    password=os.getenv("SF_PASSWORD"), 
    security_token=os.getenv("SF_SECURITY_TOKEN"), 
    domain=os.getenv("SF_DOMAIN", "login")
)

print("Querying Salesforce for duplicate email addresses...")

# Query to find emails that appear more than once
query = """
    SELECT Email, COUNT(Id) 
    FROM Contact 
    WHERE Email != null 
    GROUP BY Email 
    HAVING COUNT(Id) > 1 
    LIMIT 10
"""

result = sf.query(query)
records = result.get('records', [])

print("\nTOP DUPLICATE EMAILS LIVE IN SALESFORCE:")
if records:
    for rec in records:
        print(f"   - {rec['Email']}: appears {rec['expr0']} times")
else:
    print(" No duplicate emails found in Salesforce!")
