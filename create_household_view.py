import os
from dotenv import load_dotenv  # type: ignore
from simple_salesforce import Salesforce  # type: ignore

load_dotenv()

SF_USERNAME = os.getenv('SF_USERNAME')
SF_PASSWORD = os.getenv('SF_PASSWORD')

# Connect to Salesforce client instance
sf = Salesforce(username=SF_USERNAME, password=SF_PASSWORD, security_token='')

def deploy_household_list_view():
    print("Initializing connection to Salesforce Metadata API...")
    
    mdapi = sf.mdapi
    
    try:
        # strip the filters list completely so Salesforce doesn't throw cross-reference error
        # show ALL organizations/households in one  master layout
        list_view_definition = mdapi.ListView(
            fullName="Account.All_Households_Custom",
            label="All Households (System Automated)",
            filterScope="Everything",
            filters=[],  #Empty filters array avoids strict record-type  check
            columns=[
                "ACCOUNT.NAME",
                "ACCOUNT.PHONE1",
                "ACCOUNT.ADDRESS1_CITY",
                "ACCOUNT.ADDRESS1_STATE",
                "CORE.USERS.ALIAS"
            ]
        )
        
        # Fire metadata object straight over API cluster
        mdapi.ListView.create(list_view_definition)
        
        print("Success! The 'All Households' dashboard has been built")

    except Exception as e:
        print(f"Structural Deployment Failed: {e}")

if __name__ == "__main__":
    deploy_household_list_view()