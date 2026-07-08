import pandas as pd
import os

RAW_FILE = 'data/raw_constant_contact_UNsubscribed.csv' # hidden from push
CLEAN_FILE = 'data/clean_UNSUBSCRIBED_import.csv' # hidden from push

def clean_unsubs():
    if not os.path.exists(RAW_FILE):
        print(f"Error: Could not find {RAW_FILE}")
        return

    print("Processing unsubscribed list...") # validates if the list is being checked
    df = pd.read_csv(RAW_FILE, on_bad_lines='skip', low_memory=False)
    
    # Only track Email address for the blocklist
    if 'Email address' in df.columns: 
        # Drop rows missing an email, keep only the email column, and purge duplicates
        clean_df = df[['Email address']].dropna(subset=['Email address']).drop_duplicates()
        
        clean_df.to_csv(CLEAN_FILE, index=False)
        print(f"Success! Saved {len(clean_df)} unique unsubscribed emails to {CLEAN_FILE}")
    else:
        print("Error: Could not find 'Email address' column in the file.")

if __name__ == '__main__':
    clean_unsubs()
