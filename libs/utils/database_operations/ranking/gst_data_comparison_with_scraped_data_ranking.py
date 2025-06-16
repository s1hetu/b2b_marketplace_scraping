"""
Compare gst data with scraped data, increment score if data matches,
and override scraped data with gst data address and gst registration date.
"""
from difflib import SequenceMatcher
from pymongo import UpdateOne
from database import db

from libs.utils.config import RAW_SCRAPED_DATA_COLLECTION, GST_DATA_COLLECTION
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("gst_data_comparison_with_scraped_data_ranking")

gst_data_collection = db.get_or_create_collection(GST_DATA_COLLECTION)
scraped_data_collection = db.get_or_create_collection(RAW_SCRAPED_DATA_COLLECTION)
scraped_data_with_gst_values = (db.get_or_create_collection(RAW_SCRAPED_DATA_COLLECTION).
                                find({"gst": {"$ne": None}}).to_list())


def get_comparison_value(gst_data, scraped_data):
    """
    Get values from gst data and scraped data
    :param gst_data: The gst data
    :param scraped_data: The scraped data
    :return: dictionary with key and values from gst_data nad scraped_data
    """
    try:
        return {
            "registration_date":
                [gst_data.get("gstDetails").get("rgdt"),
                 scraped_data.get("gstRegistrationDate")],
            "company_name":
                [gst_data.get("gstDetails").get("tradeNam").lower(),
                 scraped_data.get("company").lower()],
            # "owner_name":
            #     [gst_data.get("gstDetails").get("lgnm").lower(),
            #      scraped_data.get("owner").lower()],
            "address":
                [gst_data.get("gstDetails").get("pradr").get("adr").lower(),
                 scraped_data.get("address").lower()],
        }
    except Exception as error:
        logger.error(f"Error occurred while fetching values - {error}.")


def compare_values_and_update_scraped_data(scraped_data):
    """
    Compare the values of scraped data and gst data, and
    :param scraped_data: the details for a vendor from scraped data
    :return: Dictionary with data to override

    TOTAL: 35
    current_gst_data_score : [0-10]
    comparison_score : [0-3]
    current_scraped_data_score : [0-21]
    """
    gst = scraped_data.get("gst")
    gst_data = gst_data_collection.find_one({"gst": gst})
    if not gst_data:
        logger.error(f"Unable to find data for {gst} GST Number.")
        return None

    comparison_values = get_comparison_value(gst_data, scraped_data)
    comparison_score = 0
    total_score = 0
    for key, values in comparison_values.items():
        try:
            if key in ["registration_date", "company_name"]:
                if values[0] == values[1] and values[0]:
                    comparison_score += 1
            elif key == "address":
                match_ratio = SequenceMatcher(None, values[0], values[1]).ratio()
                if match_ratio > 0.8:
                    comparison_score += 1
        except Exception as error:
            logger.error(f"Error comparing values for key '{key}': {error}")

    current_scraped_data_score = scraped_data.get("score", 0)
    current_gst_data_score = gst_data.get("score", 0)
    total_score = current_scraped_data_score + current_gst_data_score + comparison_score

    return {
        "gst_data": {
            "gstDetails": gst_data.get("gstDetails"),
            "returnDetails": gst_data.get("returnDetails"),
        },
        "score": total_score,
        "address": gst_data.get("gstDetails", {}).get("pradr", {}).get("adr", ""),
        "gstRegistrationDate": gst_data.get("gstDetails", {}).get("rgdt", ""),
        "scraped_data_score": current_scraped_data_score,
        "gst_score": current_gst_data_score,
        "gst_scraped_comparison": comparison_score,
    }

def main():
    """
    Update score based on value match and override scraped data with gst data
    for each company having gst number
    """
    operations = []
    for company_data in scraped_data_with_gst_values:

        vendor_id = company_data.get("vendorId")
        try:
            updated_data = compare_values_and_update_scraped_data(company_data)
            if updated_data:
                operations.append(UpdateOne(
                    filter={"vendorId": vendor_id},
                    update={"$set": updated_data}
                ))
        except Exception as error:
            logger.error(f"Error while updating record for vendor ID - {vendor_id} : {error}")
    logger.info("Applying new scores to DB.")
    try:
        db.bulk_write_data(RAW_SCRAPED_DATA_COLLECTION, operations)
        logger.info("Applied scores on the DB.")
    except Exception as error:
        logger.error(f"Error while bulk write data - {error}")


if __name__ == "__main__":
    main()
