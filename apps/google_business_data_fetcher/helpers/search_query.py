"""
This file contains code to fetch data from a MongoDB collection and generate search queries.
"""
import json
from database import db
from libs.utils.config import RAW_SCRAPED_DATA_COLLECTION, GOOGLE_BUSINESS_DATA_DIR_PATH
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("search_query")

def fetch_from_db():
    """
    Fetches records from the database and generates search queries.

    This function retrieves all records from the specified MongoDB collection
    and constructs search query strings based on the company name and pincode.
    It then writes these search queries to a JSON file and returns them as a list.

    Args:
        None
        
    Returns:
        list: A list of dictionaries containing 'vendorId' and 'search_string' keys.
    """

    search_strings = []
    try:
        collection = db.get_or_create_collection(RAW_SCRAPED_DATA_COLLECTION)
        all_records = list(collection.find({}))
        logger.info(f"Fetched all records from collection {RAW_SCRAPED_DATA_COLLECTION}")
        for each_record in all_records:
            try:
                company_name = each_record.get('company')
                pincode = each_record.get('pincode')
                vendorId = each_record.get('vendorId')
                if not pincode:     # cases may arise where address, gmap, and pincode are null
                    search_string = company_name+ ", Mumbai"
                else:
                    search_string = company_name+ ", Mumbai, "+ str(pincode)

                google_vendor_dict = {
                    'vendorId': vendorId,
                    'search_string': search_string
                }
                search_strings.append(google_vendor_dict)

            except Exception as error:
                logger.error(f"Could not fetch search query due to error: {str(error)}")

        logger.info(f"Created search queries for {len(search_strings)} records")
        #to keep a record of search queries for future purposes
        with open(f"{GOOGLE_BUSINESS_DATA_DIR_PATH}/search_queries.json", 'w', encoding="utf-8") as json_file:
            json.dump(search_strings, json_file, indent=4)
        return search_strings
    
    except Exception as error:
        logger.error(f"Could not fetch search queries from database, error: {str(error)}")
        return search_strings