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

print("Querying creation timestamps...")
# Fetch the creation times of all contacts
results = sf.query_all("SELECT CreatedDate FROM Contact")
records = results.get('records', [])

# Parse dates into a Pandas dataframe to group them
df = pd.DataFrame(records)
df['CreatedDate'] = pd.to_datetime(df['CreatedDate'])

# Group by hour and minute to see the creation bursts
df['Time_Block'] = df['CreatedDate'].dt.strftime('%Y-%m-%d %H:%M')     # parsing
timeline = df['Time_Block'].value_counts().sort_index()

print("\nDATA IMPORT TIMELINE BREAKDOWN:")
print("="*45)
for time_block, count in timeline.items():
    print(f"{time_block} UTC  -->  Added {count:,} records")
print("="*45)
