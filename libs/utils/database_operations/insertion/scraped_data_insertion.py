"""
Script to insert scraped, combined and mapped data into mongoDB database
To run: python3 -m libs.utils.database_operations.scraped_data_insertion
"""
import os
import json
import re
from datetime import datetime
from database import db
from libs.utils.constants import PINCODE_PATTERN
from schema_validator.vendors import vendor_validator
from libs.utils.config import RAW_SCRAPED_DATA_COLLECTION, COMBINED_DATA_DIR_PATH
from libs.utils.data_combining.remove_companies_with_same_details import (
    remove_data_with_same_details)
from libs.utils.database_operations.common import convert_keys_to_camel_case
from libs.utils.log_services.logger import setup_logger
from libs.utils.data_combining.combine_same_categories_data_from_all_websites import (
    combine_categories_data)
logger = setup_logger("scraped-data-insertion")

def convert_fields_to_list(vendor):
    """
    Function to convert 'email', 'website', 'images', and 'phone' fields in vendor data to lists if they are null or not already lists.

    Args:
        data: List of vendor dictionaries
    
    Returns
        List of vendor dictionaries with all fields converted to lists
    """

    update_fields = {}

    try:
        email = vendor.get("email")
        if not email or not isinstance(email, list):
            update_fields["email"] = [] if email is None else [email]

        website = vendor.get("website")
        if not website or not isinstance(website, list):
            update_fields["website"] = [] if website is None else [website]

        images = vendor.get("images")
        if not images or not isinstance(images, list):
            update_fields["images"] = [] if images is None else [images]

        phone = vendor.get("phone")
        if not phone or not isinstance(phone, list):
            update_fields["phone"] = [] if phone is None else [phone]

        if update_fields:
            vendor.update(update_fields)
        
        logger.info("Successfully converted 'email', 'website', 'images', and 'phone' fields to list format.")
        
        return vendor
    except Exception as e:
        logger.error(f"Error in converting fields to list: {e}")
        return vendor


def format_categories(categories):
    """
    Combine categories data from all websites into a unified format.
    """
    categories_list = []
    try:
        if isinstance(categories, list):
            categories_list = categories
        else:
            if not categories:
                logger.info(f"No categories data found.")
            else:
                if ">" in categories:
                    categories_list = categories.split(">")
                else:
                    categories_list = categories.split(",")
            categories_list = [category.strip() for category in categories_list if category.strip()]
            if "IndiaMART" in categories_list:
                categories_list.remove("IndiaMART")
        return categories_list
    except Exception as error:
        logger.error(f"Unable to format categories - {error}")
        return categories_list


def extract_pincode_from_address(address):
    """
    Extracts a valid 6-digit pincode from the given address string.

    Args:
        address (str): The address string to extract the pincode from.

    Returns:
        str or None: The extracted pincode as a string if found, else None.
    """

    try:
        if address:
            pincode_pattern = PINCODE_PATTERN
            zip_code = re.search(pincode_pattern, address)
            if zip_code:
                logger.info("Extracted pin code from address.")
                return zip_code.group(0)
            logger.warning(f"No 6-digit pincode found in address: {address}")
        else:
            logger.info("Address was not found. "
                        "So skipping pin code fetching from address.")
        return None
    except Exception as e:
        logger.error(f"Could not extract pincode due to error: {str(e)}")
        return None


def get_scraped_data():
    """
    Retrieve and process scraped data from JSON files located in the 'final' directory.
    This function reads all JSON files in the specified directory,
    converts their keys to camelCase, adds 'createdAt' and 'updatedAt'
    timestamps to each data entry, and compiles all the data into a list.
    
    Returns:
        list: A list of dictionaries containing processed data from all JSON files.
    """

    data_to_insert = []
    try:
        json_files = os.listdir(COMBINED_DATA_DIR_PATH)

        for file in json_files:
            logger.info(f"File name: {file}")
            file = file.replace(" ","-")
            with open(f"{COMBINED_DATA_DIR_PATH}/{file}", 'r', encoding="utf-8") as json_file:
                data = json.load(json_file)
                if not data:
                    logger.warning(f"Empty JSON file: {file}, no data to insert")
                    continue
                data = convert_keys_to_camel_case(data)

                for vendor in data:
                    vendor['createdAt'] = datetime.now()
                    vendor['updatedAt'] = datetime.now()
                    pincode = vendor['pincode']
                    if not pincode or pincode == "0":
                        extracted_pincode = extract_pincode_from_address(vendor['address'])
                        vendor['pincode'] = extracted_pincode
                    vendor['categories'] = format_categories(vendor['categories'])
                    vendor = convert_fields_to_list(vendor)
                data_to_insert.extend(data)
        return data_to_insert
    except FileNotFoundError as e:
        logger.error(f"Error: {e}")
        return data_to_insert
    except Exception as e:
        logger.error(f"An error occurred in getting scraped data from file: {file} - {str(e)}")
        return data_to_insert


if __name__ == "__main__":
    categories_data = combine_categories_data()
    combined_data = get_scraped_data()
    unique_data = remove_data_with_same_details(combined_data)
    db.insert_data(collection_name=RAW_SCRAPED_DATA_COLLECTION,
                   data=unique_data, validator=vendor_validator)
