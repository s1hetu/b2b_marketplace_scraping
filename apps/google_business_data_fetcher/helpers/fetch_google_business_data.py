"""
To fetch google business data for all the collected vendorIds from database
To run:  python3 -m apps.google_business_data_fetcher.helpers.fetch_google_business_data
"""
from .search_query import fetch_from_db
import requests
import time
import json
from libs.utils.constants import LOCAL_BUSINESS_DATA_URL
from libs.utils.config import X_RAPIDAPI_KEY, X_RAPIDAPI_HOST, GOOGLE_BUSINESS_DATA_DIR_PATH
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("fetch_google_business_data")
credit_logger = setup_logger("credits_remaining")

def get_google_business_data():
    """
    Fetches Google Business data for all the collected vendorIds from database.
    
    Args:
        None
        
    Returns:
        list: A list of dictionaries containing 'vendorId' and 'data' keys where:
            vendorId (str): The vendorId whose data is retrieved.
            data (list): A list of dictionaries containing Google Business data for the vendor.
    """
    
    headers = {
        "x-rapidapi-key": X_RAPIDAPI_KEY,
        "x-rapidapi-host": X_RAPIDAPI_HOST
    }

    params = {
        "limit":5,
        "language":"en",
        "extract_emails_and_contacts": "true"
    }

    search_strings = fetch_from_db()

    google_business_data = []

    for vendor in search_strings:
        search_string = vendor.get('search_string')
        vendorId = vendor.get('vendorId')
        logger.info(f"Fetching data for vendor:{vendorId}")
        
        if not search_string:
            logger.info(f"Skipping vendor {vendorId} due to missing search string.")
            continue
        
        params['query'] = search_string
        try:
            response = requests.get(LOCAL_BUSINESS_DATA_URL, headers=headers, params=params, timeout=100)
            business_details = response.json()
            business_details_data = business_details.get('data')
            if business_details_data == None:   # arises when the business credits are over
                logger.warning("Credit limit reached, upgrade to a higher plan or change the API key.")
                current_index = search_strings.index(vendor)
                remaining_vendors = search_strings[current_index:]
                with open(f"{GOOGLE_BUSINESS_DATA_DIR_PATH}/remaining-google-business-data.json", "w", encoding="utf-8") as json_file:
                    json.dump(remaining_vendors, json_file, indent=4)
                break

            credit_logger.info(f"Credits remaining: {response.headers.get('X-RateLimit-Businesses-Remaining')}")

            response_data = {
                'vendorId': vendorId,
                'data': business_details_data
            }

            google_business_data.append(response_data)

        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching Google Business data for vendor {vendorId}: {e}")
            with open(f"{GOOGLE_BUSINESS_DATA_DIR_PATH}/remaining-google-business-data.json", "w", encoding="utf-8") as json_file:
                json.dump(vendor, json_file, indent=4)

        except Exception as err:
            logger.error(f"Error: {str(err)}")
            with open(f"{GOOGLE_BUSINESS_DATA_DIR_PATH}/remaining-google-business-data.json", "w", encoding="utf-8") as json_file:
                json.dump(vendor, json_file, indent=4)
        
        time.sleep(0.2)

    try:
        with open(f"{GOOGLE_BUSINESS_DATA_DIR_PATH}/google-business-data.json", 'w', encoding="utf-8") as json_file:
            json.dump(google_business_data, json_file, indent=4)
        logger.info("Successfully dumped data into file...")
    except Exception as e:
        logger.error(f"Error: {e}")
        with open(f"{GOOGLE_BUSINESS_DATA_DIR_PATH}/google-business-data.txt", "w", encoding="utf-8") as f:
                f.write(str(google_business_data))

    return google_business_data