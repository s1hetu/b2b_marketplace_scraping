"""
Script to compare google business data with scraped data and update the scraped data
To run: python3 -m libs.utils.database_operations.ranking.gbd_data_comparison_with_scraped_data_ranking
"""
from pymongo import UpdateOne
from database import db
from libs.utils.config import (
    RAW_SCRAPED_DATA_COLLECTION,
    GOOGLE_BUSINESS_DATA_COLLECTION,
)
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("gbd-data-comparison-with-scraped-data-ranking")


def format_websites(websites):
    """
    Format website URLs by removing common prefixes.

    Args:
        websites (str|list): Single website URL or list of URLs

    Returns:
        list: Formatted website URLs with prefixes removed
    """
    try:
        if isinstance(websites, str):
            return [
                websites.replace("https://", "")
                .replace("http://", "")
                .replace("www.", "")
            ]
        elif isinstance(websites, list):
            formatted_website = [
                w.replace("https://", "").replace("http://", "").replace("www.", "")
                for w in websites
            ]
            for website in range(len(formatted_website)):
                formatted_website[website] = formatted_website[website].split("/")[0]
            return formatted_website
        else:
            return []
    except Exception as e:
        logger.error(f"Error formatting websites: {str(e)}")
        return []


def format_phone_number(phones: list):
    """
    Format phone numbers by removing '+' prefix and country code.

    Args:
        phones (list): List of phone numbers to format

    Returns:
        list: Formatted phone numbers
    """
    try:
        for i in range(len(phones)):
            phone = phones[i].replace("+", "")
            if len(phone) == 12 and phone.startswith("91"):
                phone = phone[2:]
            phones[i] = phone  # modified inplace
    except Exception as e:
        logger.error(f"Error formatting phone numbers: {str(e)}")


def fetch_vendor_data(vendor_id, raw_sellers_collection, gbd_collection):
    """
    Fetch vendor data from Google Business Data and raw scraped data collections.

    Args:
        vendor_id (str): Vendor ID to fetch data for
        raw_sellers_collection (Collection): MongoDB collection for raw scraped data
        gbd_collection (Collection): MongoDB collection for Google Business Data

    Returns:
        matched vendor data, raw seller data, GBD score, and raw seller score
    """
    try:
        gbd_vendor = gbd_collection.find_one(
            {"vendorId": vendor_id}, {"matchedVendor": 1, "score": 1}
        )
        if not gbd_vendor:
            logger.warning(f"No GBD data found for vendorId: {vendor_id}")
            return None, None, None, None

        raw_seller = raw_sellers_collection.find_one(
            {"vendorId": vendor_id},
            {
                "email": 1,
                "phone": 1,
                "categories": 1,
                "images": 1,
                "website": 1,
                "score": 1,
                "_id": 0,
            },
        )

        matched_vendor = gbd_vendor.get("matchedVendor", {})
        gbd_score = gbd_vendor.get("score", 0)
        raw_seller_score = raw_seller.get("score", 0)

        if not matched_vendor:
            logger.warning(f"No valid GBD data found for vendorId: {vendor_id}")
            return None, None, None, None

        return matched_vendor, raw_seller, gbd_score, raw_seller_score

    except Exception as e:
        logger.error(f"Error fetching data for vendorId {vendor_id}: {e}")
        return None, None, None, None


def update_emails_and_contacts(
    matched_vendor, raw_seller, update_fields, set_fields, comparison_score
):
    """
    Update email addresses and contact information from matched vendor data.

    Args:
        matched_vendor (dict): Vendor data from Google Business Data
        raw_seller (dict): Raw seller data from database
        update_fields (dict): Fields to be updated
        set_fields (dict): Fields to be set
        comparison_score (int): Current comparison score

    Returns:
        int: Updated comparison score
    """
    try:
        emails_and_contacts = matched_vendor.get("emails_and_contacts", {})

        gbd_emails = emails_and_contacts.get("emails", []) or []
        raw_seller_emails = raw_seller.get("email", []) or []

        for gbd_email in gbd_emails:
            if gbd_email in raw_seller_emails:
                comparison_score += 1
        update_fields["email"] = {"$each": gbd_emails}

        gbd_phones = emails_and_contacts.get("phone_numbers", []) or []
        raw_seller_phones = raw_seller.get("phone", []) or []
        new_phones = list(set(raw_seller_phones + gbd_phones))
        format_phone_number(new_phones)
        set_fields["phone"] = new_phones

    except Exception as e:
        logger.error(f"Error updating emails and contacts: {e}")
    return comparison_score


def update_categories(matched_vendor, raw_seller, update_fields):
    """
    Update categories from matched vendor data.

    Args:
        matched_vendor (dict): Vendor data from Google Business Data
        raw_seller (dict): Raw seller data from database
        update_fields (dict): Fields to be updated
    """
    try:
        gbd_categories = [matched_vendor.get("type", "")] + (
            matched_vendor.get("subtypes", []) or []
        )
        if gbd_categories:
            update_fields["categories"] = {"$each": gbd_categories}

    except Exception as e:
        logger.error(f"Error updating categories: {e}")


def update_websites(matched_vendor, raw_seller, set_fields, comparison_score):
    """
    Update websites from matched vendor data.

    Args:
        matched_vendor (dict): Vendor data from Google Business Data
        raw_seller (dict): Raw seller data from database
        set_fields (dict): Fields to be updated
        comparison_score (int): Current comparison score

    Returns:
        int: Updated comparison score
    """
    try:
        gbd_website = format_websites(matched_vendor.get("website"))
        raw_websites = format_websites(raw_seller.get("website"))
        all_websites = list(set(gbd_website + raw_websites))
        set_fields["website"] = all_websites
        if gbd_website and gbd_website[0] in raw_websites:
            comparison_score += 1
    except Exception as e:
        logger.error(f"Error updating websites: {e}")
    return comparison_score


def update_images(matched_vendor, raw_seller, update_fields):
    """
    Update images from matched vendor data.

    Args:
        matched_vendor (dict): Vendor data from Google Business Data
        raw_seller (dict): Raw seller data from database
        update_fields (dict): Fields to be updated
    """
    photo_urls_list = []
    try:
        gbd_images = matched_vendor.get("photos_sample", []) or []

        for photo in gbd_images:
            photo_url = photo.get("photo_url")
            if photo_url:
                photo_urls_list.append(photo_url)

        if photo_urls_list:
            update_fields["images"] = {"$each": photo_urls_list}

    except Exception as e:
        logger.error(f"Error updating images: {e}")


def apply_updates(vendor_id, update_fields, set_fields, raw_sellers_collection):
    """
    Apply updates to the raw seller data.

    Args:
        vendor_id (str): Vendor ID to update
        update_fields (dict): Fields to be updated
        set_fields (dict): Fields to be set
        raw_sellers_collection (Collection): MongoDB collection for raw scraped data
    """
    try:
        if update_fields:
            raw_sellers_collection.update_one(
                {"vendorId": vendor_id},
                {"$set": set_fields, "$addToSet": update_fields},
            )
            logger.info(f"Updated vendor {vendor_id} with new data: {update_fields}")
        else:
            logger.info(f"No new data to update for vendorId: {vendor_id}")

    except Exception as e:
        logger.error(f"Error applying updates for vendorId {vendor_id}: {e}")


def extend_existing_data():
    """
    Extend existing data with new data from Google Business Data.
    """
    bulk_operations = []
    try:
        raw_sellers_collection = db.get_or_create_collection(RAW_SCRAPED_DATA_COLLECTION)
        gbd_collection = db.get_or_create_collection(GOOGLE_BUSINESS_DATA_COLLECTION)

        vendor_ids = raw_sellers_collection.distinct("vendorId")

        for vendor_id in vendor_ids:
            matched_vendor, raw_seller, gbd_score, raw_seller_score = fetch_vendor_data(
                vendor_id, raw_sellers_collection, gbd_collection
            )
            if not matched_vendor or not raw_seller:
                continue

            update_fields = {}
            set_fields = {}
            comparison_score = 0

            comparison_score = update_emails_and_contacts(
                matched_vendor, raw_seller, update_fields, set_fields, comparison_score
            )
            comparison_score = update_websites(
                matched_vendor, raw_seller, set_fields, comparison_score
            )
            update_categories(matched_vendor, raw_seller, update_fields)
            update_images(matched_vendor, raw_seller, update_fields)
            apply_updates(vendor_id, update_fields, set_fields, raw_sellers_collection)

            # Overwrite existing fields in raw sellers
            opening_status = matched_vendor.get("opening_status")
            rating = str(matched_vendor.get("rating"))
            reviews = str(matched_vendor.get("review_count"))

            # New fields to be added
            working_hours = matched_vendor.get("working_hours")
            instagram = matched_vendor.get("emails_and_contacts", {}).get("instagram")
            facebook = matched_vendor.get("emails_and_contacts", {}).get("facebook")
            youtube = matched_vendor.get("emails_and_contacts", {}).get("youtube")
            place_link = matched_vendor.get("place_link")
            district = matched_vendor.get("district")
            google_verified = matched_vendor.get("verified")

            # Total GBD score
            total_score = raw_seller_score + gbd_score + comparison_score

            bulk_operations.append(
                UpdateOne(
                    {"vendorId": vendor_id},
                    {
                        "$set": {
                            "timings": opening_status,
                            "rating": rating,
                            "totalReviews": reviews,
                            "workingHours": working_hours,
                            "instagram": instagram,
                            "facebook": facebook,
                            "youtube": youtube,
                            "placeLink": place_link,
                            "district": district,
                            "googleVerified": google_verified,
                            "gbd_score": gbd_score,
                            "gbd_scraped_comparison": comparison_score,
                            "score": total_score,
                        }
                    },
                    upsert=True,
                )
            )

        if bulk_operations:
            result = raw_sellers_collection.bulk_write(bulk_operations)
            logger.info(
                f"Bulk write completed. Matched: {result.matched_count}, "
                f"Modified: {result.modified_count}, "
                f"Upserted: {len(result.upserted_ids)}"
            )
        else:
            logger.info("No bulk operations to perform.")

    except Exception as e:
        logger.error(f"Error: {str(e)}")

if __name__ == "__main__":
    extend_existing_data()
