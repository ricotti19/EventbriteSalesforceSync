import os
import pandas as pd
from dotenv import load_dotenv
from simple_salesforce import Salesforce

load_dotenv()

def run_live_audit():
    print("🔌 Connecting to Salesforce for a fresh audit...")
    try:
        sf = Salesforce(
            username=os.getenv("SF_USERNAME"), 
            password=os.getenv("SF_PASSWORD"), 
            security_token=os.getenv("SF_SECURITY_TOKEN"), 
            domain=os.getenv("SF_DOMAIN", "login")
        )
        print("✅ Connected successfully!")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return

    print("\n📊 Running Database Queries (this takes a moment)...")
    
    # 1. Get the global counts
    total_contacts = sf.query("SELECT COUNT(Id) FROM Contact")['records'][0]['expr0']
    unsubscribed_contacts = sf.query("SELECT COUNT(Id) FROM Contact WHERE HasOptedOutOfEmail = True")['records'][0]['expr0']
    subscribed_contacts = sf.query("SELECT COUNT(Id) FROM Contact WHERE HasOptedOutOfEmail = False")['records'][0]['expr0']

    # 2. Pull a sample of the most recently updated Opt-Outs to verify names
    print("🔍 Fetching a sample of recently flagged Unsubscribed contacts...")
    recent_unsubs = sf.query(
        "SELECT FirstName, LastName, Email, LastModifiedDate "
        "FROM Contact "
        "WHERE HasOptedOutOfEmail = True "
        "ORDER BY LastModifiedDate DESC LIMIT 10"
    )
    
    # --- PRINT THE AUDIT REPORT ---
    print("\n" + "="*40)
    print("🚨 LIVE SALESFORCE CONTACT AUDIT REPORT 🚨")
    print("="*40)
    print(f"📈 Total Contacts in Org:       {total_contacts:,}")
    print(f"🟢 Active Subscribers (False):  {subscribed_contacts:,}")
    print(f"🔴 Unsubscribed (True):         {unsubscribed_contacts:,}")
    print("-"*40)
    
    print("\n👀 SAMPLE OF RECENTLY FLIPPED OPT-OUTS:")
    records = recent_unsubs.get('records', [])
    if records:
        for idx, rec in enumerate(records):
            first = rec.get('FirstName') or ""
            last = rec.get('LastName') or ""
            email = rec.get('Email') or "No Email"
            print(f" {idx+1}. {first} {last} ({email})")
    else:
        print(" ❓ No records found with HasOptedOutOfEmail = True.")
        
    print("="*40)

if __name__ == "__main__":
    run_live_audit()