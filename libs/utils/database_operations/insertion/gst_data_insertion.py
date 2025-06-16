"""
Script to insert GST data into mongoDB collection
To run: python3 -m libs.utils.database_operations.gst_data_insertion
"""
import json
from datetime import datetime
from database import db
from libs.utils.config import GST_DIR_PATH, GST_DATA_COLLECTION
from schema_validator.gst import gst_validator
from libs.utils.database_operations.common import convert_keys_to_camel_case
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("gst-data-insertion")

def get_gst_data():
    """
    Reads the GST data from the JSON file and inserts it into the MongoDB collection.
    Args:
        None

    Returns:
        list: GST data to be inserted into the MongoDB collection.
    """
    try:
        with open(f"{GST_DIR_PATH}/gst_details_data.json", 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)
            if not data:
                logger.error(f"Empty JSON file: No data to insert")
            data = convert_keys_to_camel_case(data)

            for gst_detail in data:
                gst_detail['createdAt'] = datetime.now()
                gst_detail['updatedAt'] = datetime.now()
        return data
    
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        return []
    except Exception as e:
        logger.error(f"An error occurred in getting GST data from file: {str(e)}")
        return []

if __name__ == "__main__":
    data_to_insert = get_gst_data()
    db.insert_data(collection_name=GST_DATA_COLLECTION, data=data_to_insert, validator=gst_validator, indexes=[{"field": "gst", "unique": True}])