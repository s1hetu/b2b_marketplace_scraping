"""
Module to find the matching vendor for each vendor_id, from multiple google business data records
"""
from thefuzz import fuzz
from pymongo import UpdateOne
from database import db
from libs.utils.config import RAW_SCRAPED_DATA_COLLECTION, GOOGLE_BUSINESS_DATA_COLLECTION, GOOGLE_BUSINESS_DATA_DIR_PATH
from libs.utils.constants import NAME_MATCH_THRESHOLD, ADDRESS_MATCH_THRESHOLD
import json
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("match-vendor")

def perform_matching():
    """
    Matches the vendorId from the raw scraped data with the vendorId in the Google Business Data.
   
    Args:
        None

    Returns:
        dict: A dictionary containing the vendorId and the matched data.
    """
    matches = []
    unmatched = []
    vendor_data_mapping = {}

    try:
        raw_sellers_collection = db.get_or_create_collection(RAW_SCRAPED_DATA_COLLECTION)
        gbd_collection = db.get_or_create_collection(GOOGLE_BUSINESS_DATA_COLLECTION)
        
        raw_sellers = raw_sellers_collection.find().to_list()

        for raw_seller in raw_sellers:
            try:
                vendor_id = raw_seller.get('vendorId')
                raw_company_name = raw_seller.get('company')
                raw_address = raw_seller.get('address')

                google_data = gbd_collection.find_one({'vendorId': vendor_id})

                if not google_data:
                    unmatched.append({
                        'vendorId': vendor_id,
                        'raw_company_name': raw_company_name,
                        'raw_address': raw_address,
                        'reason': f'No matching vendorId found for {vendor_id} in Google Business Data.'
                    })
                    logger.warning(f"No Google Business Data found for VendorID: {vendor_id}")
                    continue

                name_matches = []
                for data in google_data.get('data', []):
                    google_company_name = data.get('name')
                    name_similarity = fuzz.token_set_ratio(raw_company_name, google_company_name)

                    if name_similarity >= NAME_MATCH_THRESHOLD:
                        name_matches.append({
                            'google_company_name': google_company_name,
                            'google_address': data.get('full_address'),
                            'name_similarity': name_similarity,
                            'original_data': data
                        })

                if not name_matches:
                    unmatched.append({
                        'vendorId': vendor_id,
                        'raw_company_name': raw_company_name,
                        'raw_address': raw_address,
                        'reason': f'No name match found out of {len(google_data.get("data", []))} records.'
                    })
                    logger.warning(f"No name match found for VendorID: {vendor_id}")
                    continue

                best_address_match = None
                for match in name_matches:
                    google_address = match.get('google_address')
                    address_similarity = fuzz.token_set_ratio(raw_address, google_address)

                    if address_similarity >= ADDRESS_MATCH_THRESHOLD:
                        if not best_address_match or address_similarity > best_address_match.get('token_address_similarity'):
                            best_address_match = {
                                'vendorId': vendor_id,
                                'raw_company_name': raw_company_name,
                                'google_company_name': match['google_company_name'],
                                'name_similarity': match['name_similarity'],
                                'raw_address': raw_address,
                                'google_address': google_address,
                                'token_address_similarity': address_similarity,
                                'original_data': match['original_data']
                            }

                if best_address_match:
                    matches.append(best_address_match)
                    logger.info(f"VendorID: {vendor_id}"
                                f"Name Similarity: {best_address_match['name_similarity']}%\n"
                                f"Address Similarity: {best_address_match['token_address_similarity']}%")
                    vendor_data_mapping[vendor_id] = best_address_match['original_data']

                else:
                    unmatched.append({
                        'vendorId': vendor_id,
                        'raw_company_name': raw_company_name,
                        'raw_address': raw_address,
                        'reason': f'No address match found out of {len(google_data.get("data", []))} records.'
                    })
                    logger.warning(f"No address match found for VendorID: {vendor_id}")

            except Exception as e:
                logger.error(f"Error processing VendorID: {raw_seller.get('vendorId', 'Unknown')} - {str(e)}")
                unmatched.append({
                    'vendorId': raw_seller.get('vendorId'),
                    'raw_company_name': raw_seller.get('company'),
                    'raw_address': raw_seller.get('address'),
                    'reason': f"Error during processing: {str(e)}"
                })

        with open(f'{GOOGLE_BUSINESS_DATA_DIR_PATH}/vendor_matches.json', 'w', encoding='utf-8') as json_file:
            json.dump(matches, json_file, indent=4)

        with open(f'{GOOGLE_BUSINESS_DATA_DIR_PATH}/no_matches.json', 'w', encoding='utf-8') as json_file:
            json.dump(unmatched, json_file, indent=4)

        logger.info(f"The length of matched vendors is: {len(matches)} and results saved in vendor_matches.json file.")
        logger.info(f"The length of unmatched vendors is: {len(unmatched)} and results saved in no_matches.json file.")

        total_vendors = len(matches) + len(unmatched)
        if total_vendors != len(raw_sellers):
            logger.warning("Mismatch occurred:"
                           "total number of vendors in Google business data is not equal to total number of raw sellers.")

    except Exception as e:
        logger.error(f"Critical error in perform_matching function: {str(e)}")

    return vendor_data_mapping
