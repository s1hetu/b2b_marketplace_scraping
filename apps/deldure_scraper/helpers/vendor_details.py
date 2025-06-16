"""
Spider to parse the urls and fetch data.
"""
import json
import os
import scrapy
from scrapy.crawler import CrawlerProcess
from dotenv import load_dotenv
from libs.utils.log_services.logger import setup_logger
from libs.utils.config import DELDURE_OUTPUT_DIR_PATH, PROXIES
from libs.utils.constants import (
    HEADERS,
    COOKIES,
    DELDURE_SCRAPY_CUSTOM_SETTINGS,
)

load_dotenv()
logger = setup_logger("deldure_vendor_details")


class VendorDetailsSpider(scrapy.Spider):
    """
    The spider is responsible for scraping vendor details from a list of URLs.
    """
    name = "vendor_details"

    def __init__(self, *args, urls=None, material=None, **kwargs):
        """
        Initializes the spider with the given urls and material. If urls is not provided, it defaults to an empty list.
        """
        super(VendorDetailsSpider, self).__init__(*args, **kwargs)
        self.urls = urls or []
        self.material = material

    headers = HEADERS

    cookies = COOKIES

    custom_settings = DELDURE_SCRAPY_CUSTOM_SETTINGS

    proxies = PROXIES

    def start_requests(self):
        """
        Processes a list of URLs and initiates Scrapy requests.
        """
        for url in self.urls:
            url = url.strip()
            logger.info(f"Processing URL:{url}")
            yield scrapy.Request(
                url,
                callback=self.parse,
                headers=self.headers,
                cookies=self.cookies,
                meta={"material": self.material, "proxy": self.proxies["http"]},
            )

    def parse(self, response):
        """
        Processes JSON response and saves vendor details to a file.
        """
        try:
            material = response.meta.get("material")  # Retrieve 'material' from meta
        except Exception as e:
            logger.error(f"Error: {e}")
        if response.status == 200:
            try:
                vendor_data = response.json()  # Assumes the response is JSON
                if vendor_data['city'] == "Mumbai":
                    vendor_data = self.filter_and_modify_vendor_data(vendor_data)
                    vendor_details = {
                        "vendorId": vendor_data.get("vendorId"),
                        "vendorDisplayName": vendor_data.get("vendorName"),
                        "vendorAddress": vendor_data.get("address"),
                        "vendorLocality": vendor_data.get("locality"),
                        "vendorCity": vendor_data.get("city"),
                        "vendorState": vendor_data.get("stateName"),
                        "vendorCountry": vendor_data.get("countryName"),
                        "vendorZip": vendor_data.get("zip"),
                        "emailId": vendor_data.get("emailId"),
                        "vendorCategoryFolio": vendor_data.get("categoryFolio"),
                        "phone": vendor_data.get("phone"),
                        "website": vendor_data.get("website"),
                        "isActive": vendor_data.get("isActive"),
                        "dataSource": vendor_data.get("dataSource"),
                    }

                    # Save to file
                    file_name = material.replace(" ", "-")
                    file_path = f"{DELDURE_OUTPUT_DIR_PATH}/{file_name}.json"

                    # Check if file exists and load existing data
                    if os.path.exists(file_path):
                        with open(file_path, "r", encoding="utf-8") as f:
                            vendor_details_list = json.load(f)  # Load existing JSON list
                    else:
                        vendor_details_list = []  # Start with an empty list if file doesn't exist

                    # Append the new JSON object
                    vendor_details_list.append(vendor_details)

                    # Write the updated list back to the file
                    with open(file_path, "w", encoding="utf-8") as f:
                        json.dump(vendor_details_list, f, ensure_ascii=False, indent=4)
                        logger.info(
                            f"Saved vendor data for ID: {vendor_details['vendorId']}"
                        )
                else:
                    logger.info(f"Skipping data as its not of Mumbai.")

            except json.JSONDecodeError:
                logger.error(f"Failed to decode JSON response from {response.url}")

            except Exception as e:
                logger.error(f"Failed to process response from {response.url}. Error: {str(e)}")

        else:
            logger.error(
                f"Failed to fetch vendor details, status: {response.status}"
            )

    @staticmethod
    def filter_and_modify_vendor_data(vendor_data):

        # replace dashes in values with empty strings
        for key in vendor_data:
            if vendor_data[key] == "-":
                vendor_data[key] = ""
        phone_list = [
            phone
            for phone in [
                vendor_data.get("phone1"),
                vendor_data.get("phone2"),
            ] if phone
        ]

        actual_numbers = []
        for phone in phone_list:
            if phone:
                phone = phone.replace("-", "").replace("(", "").replace(")", "")
                phone = "".join(phone.split())
                if len(phone) > 10:
                    phone = phone[1:11]
                if len(phone) == 9:
                    phone = phone[1:]
                if len(phone) == 8:
                    actual_numbers.append(f"22{phone}")
                actual_numbers.append(phone)
        vendor_data['phone'] = list(set(actual_numbers))

        # delete the original phone1 and phone2 keys
        del vendor_data['phone1']
        del vendor_data['phone2']
        return vendor_data


if __name__ == "__main__":
    logger.getLogger("scrapy").setLevel(logger.WARNING)
    logger.getLogger("scrapy").propagate = False
    process = CrawlerProcess(
        {
            "USER_AGENT": HEADERS['User-Agent']
        }
    )

    process.crawl(VendorDetailsSpider)
    process.start()
