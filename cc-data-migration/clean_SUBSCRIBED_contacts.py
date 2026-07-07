import pandas as pd # dependency 1
import os # dependency 2

# Defining the "clean" and "dirty" data files
RAW_FILE = 'data/raw_constant_contact_subscribed.csv'
CLEAN_FILE = 'data/clean_SUBSCRIBED_import.csv'

def clean_data():
    if not os.path.exists(RAW_FILE):
        print(f"Error: Could not find {RAW_FILE}. Make sure the file is in the right folder!")
        return

    print("Reading raw Constant Contact export")
    
    # Read the CSV file
    # error_bad_lines/on_bad_lines helps bypass rows broken by raw text multi-line notes
    df = pd.read_csv(RAW_FILE, on_bad_lines='skip', low_memory=False)
    
    # These exact strings match the headers you provided
    columns_to_keep = [
        'Email address', 
        'First name', 
        'Last name', 
        'Full name',
        'Phone - mobile', 
        'City - Home', 
        'State/Province - Home',
        'Tags', 
        'Email Lists', 
        'Created At'
    ]
    
    # Filter only the columns that actually exist in the file to prevent crashes
    existing_columns = [col for col in columns_to_keep if col in df.columns]
    
    print(f"🧹 Trimming down from {len(df.columns)} columns to {len(existing_columns)} target columns...")
    clean_df = df[existing_columns].copy()
    
    # to handle missing or empty text values
    text_cols = ['First name', 'Last name', 'Full name', 'Tags', 'Email Lists']
    for col in text_cols:
        if col in clean_df.columns:
            clean_df[col] = clean_df[col].fillna('')
            
    # Drop rows that are completely empty or missing an email address
    if 'Email address' in clean_df.columns:
        clean_df = clean_df.dropna(subset=['Email address'])
    
    # Remove duplicate entries based on email address
    clean_df = clean_df.drop_duplicates(subset=['Email address'], keep='first')
    
    # Save the polished data
    clean_df.to_csv(CLEAN_FILE, index=False)
    print(f"Success! Cleaned file saved to: {CLEAN_FILE}")
    print(f"Extracted {len(clean_df)} unique contacts.")

if __name__ == '__main__':
    clean_data()