import os
import sys
import logging
from datetime import datetime
from dotenv import load_dotenv  # type: ignore
from simple_salesforce import Salesforce  # type: ignore

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
load_dotenv()

SF_USERNAME = os.getenv('SF_USERNAME')
SF_PASSWORD = os.getenv('SF_PASSWORD')

def run_campaign_cleanup():
    try:
        sf = Salesforce(username=SF_USERNAME, password=SF_PASSWORD, security_token='')
    except Exception as e:
        logging.error(f"Salesforce Login block: {e}")
        return

    logging.info("Fetching all campaigns from Salesforce...")
    
    # Query all campaigns with their IDs, Names, EndDates, and current Active status
    query = "SELECT Id, Name, EndDate, IsActive FROM Campaign"
    results = sf.query_all(query)
    campaigns = results.get('records', [])
    
    current_year = datetime.now().year
    logging.info(f"Found {len(campaigns)} total campaigns. Starting analysis...")

    for campaign in campaigns:
        campaign_id = campaign['Id']
        name = campaign['Name']
        end_date_str = campaign.get('EndDate')
        is_active = campaign['IsActive']
        
        # Determine year of the campaign
        campaign_year = None
        if end_date_str:
            # EndDate comes back as YYYY-MM-DD
            campaign_year = int(end_date_str.split('-')[0])
        else:
            # Backup: If no end date is set, try to guess if there's a 4-digit year in the title
            words = name.split()
            for word in words:
                if word.isdigit() and len(word) == 4:
                    campaign_year = int(word)
                    break

        # Cleanup Logic
        if campaign_year and campaign_year < current_year:
            # It's an old campaign
            if is_active:
                logging.info(f"Archiving old campaign: '{name}' ({campaign_year})")
                sf.Campaign.update(campaign_id, {'IsActive': False})
        else:
            # It's a recent/current campaign
            if not is_active:
                logging.info(f"Restoring/Keeping active: '{name}'")
                sf.Campaign.update(campaign_id, {'IsActive': True})

    logging.info("Salesforce cleanup complete! Old data is archived and recent data is visible.")

if __name__ == "__main__":
    if not all([SF_USERNAME, SF_PASSWORD]):
        logging.error("Missing Salesforce credentials in .env file.")
        sys.exit(1)
        
    run_campaign_cleanup()
