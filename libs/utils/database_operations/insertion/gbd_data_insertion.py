"""
Script to insert google business data into mongoDB collection
To run: python3 -m libs.utils.database_operations.gbd_data_insertion
"""
import json
from datetime import datetime
from database import db
from libs.utils.config import GOOGLE_BUSINESS_DATA_COLLECTION, GOOGLE_BUSINESS_DATA_DIR_PATH
from schema_validator.google_business_data import gbd_validator
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("gbd-data-insertion")

def get_gbd_data():
    """
    Fetches google business data from collection and adds the createdAt and updatedAt fields.
    Args:
        None
    Returns:
        list: A list of dictionaries containing processed data.
    """
    try:
        with open(f"{GOOGLE_BUSINESS_DATA_DIR_PATH}/google-business-data.json", 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
            if not data:
                logger.error("Empty JSON file: No data to insert")

            for gbd_data in data:
                gbd_data['createdAt'] = datetime.now()
                gbd_data['updatedAt'] = datetime.now()
        return data
    
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        return []
    except Exception as e:
        logger.error(f"An error occurred in getting GBD data from file: {str(e)}")
        return []
    
if __name__ == "__main__":
    data_to_insert = get_gbd_data()
    db.insert_data(collection_name=GOOGLE_BUSINESS_DATA_COLLECTION,
                   data=data_to_insert,
                   validator=gbd_validator,
                   indexes=[{"field": "vendorId", "unique": True}])