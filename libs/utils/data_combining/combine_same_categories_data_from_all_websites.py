"""
Combine website data for each category
to run the file: 
python3 -m libs.utils.data_combining.combine_data_from_all_websites
"""
import json
import os
from dotenv import load_dotenv
from libs.utils.constants import MATERIALS, DATA_COMPARISON_DICT
from libs.utils.config import COMBINED_DATA_DIR_PATH, OUTPUT_DIR
from libs.utils.log_services.logger import setup_logger

logger =  setup_logger("combine-data")

load_dotenv()

def field_mapping(company, website):
    """
    Function to map fields from all websites.
    :param company: Company Object
    :param website: Name of website
    :return: Dict with values
    """
    mapping = {
        "Deldure": {
            "Vendor ID": company.get("vendorId"),
            "Source": "Deldure",
            "Company": company.get("vendorDisplayName"),
            "Company description": None,
            "Address": company.get("vendorAddress"),
            "Locality": company.get("vendorLocality"),
            "City": company.get("vendorCity"),
            "State": company.get("vendorState"),
            "Country": company.get("vendorCountry"),
            "Pincode": company.get("vendorZip"),
            "Email": company.get("emailId"),
            "Categories": company.get("vendorCategoryFolio"),
            "Phone": company.get("phone"),
            "Website": company.get("website"),
            "Rating": None,
            "Total Reviews": None,
            "Year of Establishment": None,
            "Turnover": None,
            "GST": None,
            "GST Registration Date": None,
            "Owner": None,
            "Number of Employees": None,
            "GMAPS": None,
            "Images": None,
            "Timings": None,
        },
        "IndiaMart": {
            "Vendor ID": company.get("vendorId"),
            "Source":"IndiaMart",
            "Company": company.get("companyName"),
            "Company description": company.get("company_description"),
            "Address": company.get("company_address"),
            "Locality": company.get("companyRegion"),
            "City": company.get("regionSearchedFor"),
            "State": company.get("Maharashtra"),
            "Country": company.get("India"),
            "Pincode": None,
            "Email": None,
            "Categories": company.get("category"),
            "Phone": company.get("companyContactNumber"),
            "Website": company.get("companyUrl"),
            "Rating": company.get("stars"),
            "Total Reviews": company.get("users_count"),
            "Year of Establishment": company.get("company_details").get("Year of Establishment")
            if company.get("company_details") else None,
            "Turnover": company.get("company_details").get("Annual Turnover") if company.get(
                "company_details") else None,
            "GST": company.get("company_details").get("GST") if
            company.get("company_details") else None,
            "GST Registration Date": company.get("company_details").get(
                "GST Registration Date") if company.get(
                "company_details") else None,
            "Owner": company.get("seller_name"),
            "Number of Employees": company.get("company_details").get(
                "Number of Employees") if company.get(
                "company_details") else None,
            "GMAPS": company.get("gmaps"),
            "Images": company.get("product_images"),
            "Timings": None,
        },
        "JustDial": {
            "Vendor ID": company.get("extracted json").get("vendorId") if
            company.get("extracted json") else None,
            "Source":"JustDial",
            "Company": company.get("Vendor Name"),
            "Company description": None,
            "Address": company.get("extracted json").get("address") if
            company.get("extracted json") else None,
            "Locality": company.get("extracted json").get("landmark") if
            company.get("extracted json") else None,
            "City": company.get("extracted json").get("city") if
            company.get("extracted json") else None,
            "State": company.get("Maharashtra"),
            "Country": company.get("India"),
            "Pincode": company.get("extracted json").get("pincode") if
            company.get("extracted json") else None,
            "Email": company.get("email"),
            "Categories": [i.get('category') for i in
                           company.get("extracted json").get("also_listed_in")] if
            company.get("extracted json") else None,
            "Phone": company.get("extracted json").get("whatsapp number") if
            company.get("extracted json") else None,
            "Website": company.get("extracted json").get("website") if
            company.get("extracted json") else None,
            "Rating": company.get("extracted json").get("rating") if
            company.get("extracted json") else None,
            "Total Reviews": company.get("total_reviews"),
            "Year of Establishment": company.get("Business Statutory Details").get(
                "Year of Establishment") if company.get("Business Statutory Detail") else None,
            "Turnover": company.get("Business Statutory Detail").get("Turn Over") if
            company.get("Business Statutory Detail") else None,
            "GST": company.get("Business Statutory Detail").get("GSTIN") if company.get(
                "Business Statutory Detail") else None,
            "GST Registration Date": None,
            "Owner": company.get("extracted json").get("contact_person") if
            company.get("extracted json") else None,
            "Number of Employees": company.get("extracted json").get("number_of_employees")
            if company.get("extracted json") else None,
            "GMAPS": company.get("extracted json").get("directions_google_maps") if
            company.get("extracted json") else None,
            "Images": None,
            "Timings": company.get("extracted json").get("operation_hours") if
            company.get("extracted json") else None,
        }
    }
    return mapping.get(website)


def combine_categories_data():
    """
    Combine data from all websites for each category
    """
    for category in MATERIALS:
        logger.info(f"\nCATEGORY : {category}")
        data = []
        try:
            dir_path = os.path.join(os.getcwd(), OUTPUT_DIR)
            category_name = category.replace(" ", "-")
            category_name = f"{category_name}".replace(" ", "-")
            logger.info(f"Initiating  combining procedure for file: {category_name}...")

            for website in DATA_COMPARISON_DICT:
                website = website.lower()
                file_path = f"{dir_path}/{website}/{category_name}.json"
                if os.path.exists(file_path):
                    with open(file_path, 'r', encoding="utf-8") as json_file:
                        data.extend(json.load(json_file))
                else:
                    logger.warning(f"File not found for Website: {website}, file path: {file_path}")

            mapped_data = []
            for company in data:
                if company.get('vendorDisplayName'):
                    website = 'Deldure'
                elif company.get('companyName'):
                    website = "IndiaMart"
                elif company.get("Vendor Name"):
                    website = "JustDial"
                else:
                    logger.error("Error fetching company/vendor name.")

                mappings = field_mapping(company, website)
                mapped_data.append(mappings)

            with open(f"{COMBINED_DATA_DIR_PATH}/{category_name}.json", 'w',
                      encoding="utf-8") as combined_file:
                json.dump(mapped_data, combined_file, indent=4)

        except Exception as e:
            logger.error(f"Exception has occurred in combining data: {e}")
