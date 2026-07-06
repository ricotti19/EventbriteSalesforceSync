import os
import sys
import csv
import glob
import logging
from dotenv import load_dotenv  # type: ignore
from simple_salesforce import Salesforce  # type: ignore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

SF_USERNAME = os.getenv('SF_USERNAME')
SF_PASSWORD = os.getenv('SF_PASSWORD')

EXPORT_DIR = "volunteer_exports"

def validate_config():
    if not all([SF_USERNAME, SF_PASSWORD]):
        logging.error("Missing Salesforce credentials in your .env file!")
        sys.exit(1)
    if not os.path.exists(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)
        logging.info(f"Created '{EXPORT_DIR}' folder. Please drop your CSV files in there and rerun!")
        sys.exit(0)

def parse_campaign_name_from_filename(filename):
    """Extracts a campaign name from the given filename based on known patterns."""
    base_name = os.path.basename(filename).upper()
    
    # Parser: format: MONTH_MAY_YEAR_2026_SH.csv
    if "MONTH_" in base_name and "_YEAR_" in base_name:
        try:
            parts = base_name.replace(".CSV", "").split("_")
            month_idx = parts.index("MONTH") + 1
            year_idx = parts.index("YEAR") + 1
            
            month = parts[month_idx].capitalize()
            year = parts[year_idx]
            return f"{year} {month} Feeding"
        except Exception:
            pass

    # Legacy fallback parser for original June file
    if "SERVINGHOPE" in base_name or "TSOH" in base_name:
        if "JUN" in base_name and "2026" in base_name:
            return "2026 June Feeding"
            
    # Absolute fallback if filename format is totally wild
    return f"{os.path.basename(filename).replace('.csv', '').replace('.CSV', '')}"

def get_or_create_campaign(sf, campaign_name):
    """Queries Salesforce for the campaign name. Creates it if it doesn't exist."""
    clean_name = campaign_name.replace("'", "\\'")
    query = f"SELECT Id FROM Campaign WHERE Name = '{clean_name}' LIMIT 1"
    result = sf.query(query)
    
    if result['totalSize'] > 0:
        campaign_id = result['records'][0]['Id']
        logging.info(f"Found existing Salesforce Campaign: '{campaign_name}' (ID: {campaign_id})")
        return campaign_id
    else:
        logging.info(f"✨ Campaign '{campaign_name}' not found. Creating it dynamically...")
        new_campaign = sf.Campaign.create({
            'Name': campaign_name,
            'IsActive': True,
            'Type': 'Event',
            'Status': 'In Progress'
        })
        campaign_id = new_campaign['id']
        logging.info(f"Successfully created new Campaign: '{campaign_name}' (ID: {campaign_id})")
        return campaign_id

def process_single_csv(sf, file_path):
    campaign_name = parse_campaign_name_from_filename(file_path)
    campaign_id = get_or_create_campaign(sf, campaign_name)
    
    with open(file_path, mode='r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        reader.fieldnames = [name.strip() for name in reader.fieldnames] if reader.fieldnames else []
        
        rows = list(reader)
        total_volunteers = len(rows)
        logging.info(f"Processing {total_volunteers} records from file: {os.path.basename(file_path)}")

        for current_idx, row in enumerate(rows, 1):
            email = row.get('Buyer email', '').strip()
            first_name = row.get('Buyer first name', '').strip()
            last_name = row.get('Buyer last name', '').strip()
            
            if not email or not last_name:
                continue
                
            clean_email = email.replace("'", "\\'")
            progress_prefix = f"[{campaign_name}][{current_idx}/{total_volunteers}]"
            
            try:
                # 1. Check or Upsert Contact
                search_query = f"SELECT Id FROM Contact WHERE Email = '{clean_email}' LIMIT 1"
                search_result = sf.query(search_query)
                
                if search_result['totalSize'] > 0:
                    contact_id = search_result['records'][0]['Id']
                    sf.Contact.update(contact_id, {'FirstName': first_name, 'LastName': last_name})
                else:
                    new_contact = sf.Contact.create({
                        'FirstName': first_name,
                        'LastName': last_name,
                        'Email': email,
                        'LeadSource': 'Bulk Eventbrite Export'
                    })
                    contact_id = new_contact['id']
                    
                # 2. Add to dynamically identified Campaign
                cm_query = f"SELECT Id FROM CampaignMember WHERE CampaignId = '{campaign_id}' AND ContactId = '{contact_id}'"
                cm_result = sf.query(cm_query)
                
                if cm_result['totalSize'] == 0:
                    sf.CampaignMember.create({
                        'CampaignId': campaign_id,
                        'ContactId': contact_id,
                        'Status': 'Responded'
                    })
            except Exception as e:
                logging.error(f"{progress_prefix} Error processing {email}: {e}")

def main():
    validate_config()
    
    try:
        sf = Salesforce(username=SF_USERNAME, password=SF_PASSWORD, security_token='')
    except Exception as e:
        logging.error(f"Salesforce Login block: {e}")
        return

    # Scan the folder for all CSV files
    csv_files = glob.glob(os.path.join(EXPORT_DIR, "*.csv"))
    
    if not csv_files:
        logging.warning(f"No CSV files found in the '{EXPORT_DIR}' directory!")
        return

    logging.info(f"📚 Found {len(csv_files)} files to import. Starting batch processing...")
    
    for file_path in csv_files:
        logging.info(f"--- Starting file: {os.path.basename(file_path)} ---")
        process_single_csv(sf, file_path)
        logging.info(f"--- Finished file: {os.path.basename(file_path)} --- \n")

    logging.info("Master pipeline run complete! All folders synchronized ")

if __name__ == "__main__":
    main()