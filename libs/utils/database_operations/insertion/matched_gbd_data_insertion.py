from pymongo import UpdateOne
from database import db
from apps.google_business_data_fetcher.helpers.match_vendor import perform_matching
from libs.utils.config import GOOGLE_BUSINESS_DATA_COLLECTION
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("matched-gbd-data-insertion")

def update_matched_vendors_in_gbd(vendor_data_mapping):
    """
    Updates the Google Business Data collection with matched vendor data.

    This function iterates over all vendors in the Google Business Data
    collection and updates each vendor's matched data using the provided
    vendor data mapping. It performs bulk write operations to insert the 'matchedVendor' field for each vendor.

    Args:
        vendor_data_mapping (dict): A dictionary mapping vendor IDs to their
        matched vendor data.

    Returns:
        None
    """

    bulk_operations = []
    gbd_collection = db.get_or_create_collection(GOOGLE_BUSINESS_DATA_COLLECTION)
    all_vendors = gbd_collection.find()

    for vendor in all_vendors:
        try:
            vendor_id = vendor.get('vendorId')
            matched_data = vendor_data_mapping.get(vendor_id, {})

            if matched_data:
                emails_and_contacts = matched_data.get('emails_and_contacts', {})
                phone_number = matched_data.get('phone_number')

                if phone_number:
                    if 'phone_numbers' not in emails_and_contacts:
                        emails_and_contacts['phone_numbers'] = []
                    emails_and_contacts['phone_numbers'].append(phone_number)
                del matched_data['phone_number']

                matched_data['emails_and_contacts'] = emails_and_contacts

            bulk_operations.append(
                UpdateOne(
                    {'vendorId': vendor_id},
                    {'$set': {'matchedVendor': matched_data}},
                    upsert=True
                )
            )
        except Exception as e:
            logger.error(f"Error updating vendor {vendor_id}: {str(e)}")
    try:
        if bulk_operations:
            result = gbd_collection.bulk_write(bulk_operations)
            logger.info(f"Bulk write completed. Matched: {result.matched_count}, "
                        f"Modified: {result.modified_count}, "
                        f"Upserted: {len(result.upserted_ids)}")
        else:
            logger.info("No bulk operations to perform.")
    except Exception as e:
        logger.error(f"Error performing bulk write: {str(e)}")


if __name__ == "__main__":
    vendor_data_mapping = perform_matching()
    update_matched_vendors_in_gbd(vendor_data_mapping)
