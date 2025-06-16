"""
Scrapy spider to gather data from all saved urls in an async manner
"""
import os
import json
import scrapy
from libs.utils.config import JUSTDIAL_OUTPUT_DIR_PATH
from libs.utils.constants import CUSTOM_SETTINGS
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("jd_vendor_details_spider")


class DetailSpider(scrapy.Spider):
    """
    Spider to the details from URLs
    """
    name = "detail_spider"

    def __init__(self, start_urls=[], file_name: str = "details.json", *args, **kwargs):
        super(DetailSpider, self).__init__(*args, **kwargs)
        self.start_urls = start_urls
        self.file_name = file_name

    custom_settings = CUSTOM_SETTINGS

    def analyze_json(self, json_data):
        """
        Analyze the given JSON data, process it and extract the required fields.

        Args: json_data: The JSON data to be analyzed
        Returns: A dictionary containing the extracted data
        """
        try:
            main = json_data.get("props", {}).get("pageProps", {})
            main_data = None
            if main.get("cmpinfoData"):
                main_data = main["cmpinfoData"]
            elif main.get("results").get("results"):
                main_data = main["results"]["results"]
        except Exception as e:
            logger.error(f"An error occurred in analyzing json: {str(e)}")

        whatsapp_number = []  # Default value for whatsapp_number
        try:
            msg_num = main_data.get("msg_num")
            if msg_num:
                whatsapp_data = json.loads(msg_num)  # Parse the JSON string
                if (
                    "wup" in whatsapp_data and whatsapp_data["wup"]
                ):  # Check if "wup" exists and is not empty
                    whatsapp_number = whatsapp_data["wup"]
                    whatsapp_number = [str(i) for i in whatsapp_number if i]
        except (TypeError, ValueError, IndexError, KeyError) as e:
            # Handle cases where JSON parsing or indexing fails
            logger.error(f"An error occurred in extracting Whatsapp number: {str(e)}")
            whatsapp_number = []

        try:
            extracted_data = {
                "vendorId": main_data.get("common_event_data", {}).get("docid"),
                "city": main.get("city"),
                "catenated_name": main.get("catname"),
                "mobile": main.get("mobile"),
                "contact": main.get("contact"),
                "fax": main.get("fax"),
                "website": main.get("website"),
                "whatsapp_number": whatsapp_number,
                "contact_person": main_data.get("contactperson"),
                "company_name": main_data.get("name"),
                "address": main_data.get("address"),
                "email": main_data.get("email"),
                "landmark": main_data.get("landmark"),
                "latitude": main_data.get("complat"),
                "longitude": main_data.get("complong"),
                "pincode": main_data.get("pincode"),
                "gstin": main_data.get("gst_d"),
                "rating": main_data.get("comprating") or main_data.get("rating"),
                "operation_hours": main_data.get("HoursOfOperation"),
                "also_listed_in": list(
                    map(
                        lambda x: {"category": x["category"], "catid": x["catid"]},
                        main_data.get("AlsoListedIn", []),
                    )
                ),
                "mode_of_payment": main_data.get("paymentModes"),
                "total_reviews": main_data.get("totalreviews"),
                "year_of_establishment": main_data.get("YOE"),
                "services": main_data.get("services"),
                "quick_info": main_data.get("quickinfo"),
                "verified": main_data.get("verified"),
                "dp": main_data.get("disp_pic"),
                "legal_company_name": main_data.get("legal_companyname"),
                "number_of_employees": main_data.get("no_employee"),
                "turnover": main_data.get("turnover"),
                "directions_google_maps": main_data.get("sectiontab", {})
                .get("rhs", {})[0][0]
                .get("directionurl"),
                "jd_verified": main_data.get("common_event_data", {}).get(
                    "jd_verified"
                ),
                "trusted": main_data.get("common_event_data", {}).get("trusted"),
                "guarantee": main_data.get("common_event_data", {}).get("guarantee"),
                "description": main_data.get("bizinfo", {}).get("bizinfo"),
            }
            return extracted_data
        except Exception as e:
            logger.error(f"An error occurred in extracting data: {str(e)}")
            return {}

    def parse(self, response):
        """
        Parse the vendor details page and extract relevant information.

        Args:
            response: a scrapy response object

        Yields:
            A dictionary containing the extracted vendor details
        """
        try:
            vendor_name = response.css("div.vendbox_title h1::text").get()
            vendor_badges = response.css("div.vendbox_badges  div::text").getall()
            vendor_address_short = response.css(".vendbox_addres::text").getall()
            vendor_contact = response.css(".action_item_call::text").get()

            vendor_jd_verified = (
                "JD Verified" if response.css(".vend_jdverified") else None
            )
            if vendor_jd_verified and vendor_badges:
                vendor_badges.append(vendor_jd_verified)

            business_statutory_details = {}
            info_items = response.css("ul.dtl_infolist > li.dtl_infolist_item")
            for item in info_items:
                label = item.css(".dtl_labeltext::text").get()
                value = item.css(".dtl_infotext::text").get()
                if label and value:
                    business_statutory_details[label.strip()] = value.strip()

            full_address = response.css(
                "#address_rhs > div:nth-child(4) > address::text"
            ).get()

            also_listed_in = response.css('[title="Also listed in"]::text').getall()

            json_data_element = response.css("#__NEXT_DATA__::text").get()
            json_data = json.loads(json_data_element) if json_data_element else None
            extracted_json = self.analyze_json(json_data)

            extracted_data = {
                "url": response.url,
                "Vendor Name": vendor_name,
                "Vendor Badges": vendor_badges,
                "Vendor Short Address": vendor_address_short,
                "Vendor Contact": vendor_contact,
                "Business Statutory Details": business_statutory_details,
                "Full Address": full_address,
                "Also listed in": also_listed_in,
                "extracted json": extracted_json,
            }
        except Exception as e:
            logger.error(f"An error occurred in spider parsing: {str(e)}")

        file = f"{JUSTDIAL_OUTPUT_DIR_PATH}/{self.file_name}"
        if os.path.exists(file):
            with open(file, "r+") as json_file:
                try:
                    json_file.seek(0)
                    current_data = list(json.load(json_file))
                except json.JSONDecodeError:
                    current_data = []
                data = dict(extracted_data)
                current_data.append(data)

                json_file.seek(0)
                json.dump(current_data, json_file, indent=4)
        else:
            data = []
            data.append(extracted_data)
            with open(file, "w") as json_file:
                json_file.seek(0)
                json.dump(data, json_file, indent=4)
        yield extracted_data
