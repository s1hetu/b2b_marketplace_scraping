"""
Spider to parse the urls and fetch data.
"""
import json
from typing import Iterable
import scrapy
from scrapy import Request
from libs.utils.config import PROXIES, INDIAMART_SCRAPER_CUSTOM_SETTINGS
from libs.utils.constants import (VERIFIER_NAME_TEXT_XPATH,
                        CALL_RESPONSE_RATE_TEXT_XPATH,
                        PRODUCT_IMAGES_SRC_XPATH, ALTERNATE_PRODUCT_IMAGES_SRC_XPATH, PRODUCT_SPECS_XPATH,
                        PRODUCT_DESCRIPTION_TEXT_XPATH, COMPANY_DESCRIPTION_TEXT_XPATH,
                        SELLER_NAME_TEXT_XPATH, GMAPS_HREF_XPATH, COMPANY_ADDRESS_TEXT_XPATH, COMPANY_URL_HREF_XPATH,
                        COMPANY_DETAILS_XPATH, PRODUCT_CATEGORY)
from libs.utils.log_services.logger import setup_logger
from .items import ProductScraperItem

logger = setup_logger("indiamart_product_url_scraping")


class ProductScraper(scrapy.Spider):
    """
    Scrapy Spider to fetch the data from URLs.
    """
    name = 'product_spider'
    custom_settings = INDIAMART_SCRAPER_CUSTOM_SETTINGS

    def __init__(self, *args, file_name=None, extra_data=None, **kwargs):
        self.extra_data = extra_data
        self.start_urls = [i.get('productUrl') for i in self.extra_data if i.get('productUrl')]
        self.file_name = file_name
        super().__init__(*args, **kwargs)

    def start_requests(self) -> Iterable[Request]:
        """
        Processes a list of URLs and initiates Scrapy requests.
        """
        proxies = PROXIES

        for url in self.start_urls:
            yield scrapy.Request(
                url=url,
                callback=self.parse,
                meta={"proxy": proxies['http']},
            )

    def parse(self, response):
        """
        Processes a product page and extracts the required data.

        :param response: Scrapy response object
        :return: ProductScraperItem object
        """
        if response.status == 200:
            item = ProductScraperItem()
            company_extra_details = {
                'Nature of Business': None,
                'GST Registration Date': None,
                'Legal Status of Firm': None,
                'Number of Employees': None,
                'Import Export Code (IEC)': None,
                'IndiaMART Member Since': None,
                'GST': None,
                'Annual Turnover': None,
                'Year of Establishment': None,
                'Exports to': None
            }

            for i in self.extra_data:
                response_url_part = response.url.split("html?")[0]
                if response_url_part == i.get('productUrl').split("html?")[0]:
                    resp_obj = i
                    item['vendorId'] = resp_obj.get('vendorId')
                    item['searchQuery'] = resp_obj.get('searchQuery')
                    item['regionSearchedFor'] = resp_obj.get('regionSearchedFor')
                    item['companyName'] = resp_obj.get('companyName')
                    item['companyUrl'] = resp_obj.get('companyUrl')
                    item['companyRegion'] = resp_obj.get('companyRegion')
                    item['productUrl'] = resp_obj.get('productUrl')
                    item['companyContactNumber'] = resp_obj.get('companyContactNumber')
                    item['company_address'] = resp_obj.get('company_address')
                    item['stars'] = resp_obj.get('stars')
                    item['users_count'] = resp_obj.get('users_count')
                    break
            else:
                logger.info("No match")

            item['verifier_name'] = response.xpath(VERIFIER_NAME_TEXT_XPATH).get()
            item['call_response_rate'] = response.xpath(CALL_RESPONSE_RATE_TEXT_XPATH).get()
            item['seller_name'] = response.xpath(SELLER_NAME_TEXT_XPATH).get()
            item['gmaps'] = response.xpath(GMAPS_HREF_XPATH).get()
            item['product_description'] = "".join(
                [i.strip() for i in response.xpath(PRODUCT_DESCRIPTION_TEXT_XPATH).getall()])
            item['company_url'] = response.xpath(COMPANY_URL_HREF_XPATH).get()
            company_details = response.xpath(COMPANY_DETAILS_XPATH)
            for company_detail in company_details:
                company_data = company_detail.xpath("./span/text()").getall()
                if company_data and len(company_data) >= 2:
                    key = company_data[0]
                    value = company_data[1]
                    company_extra_details[key] = value

            item['company_details'] = company_extra_details

            item['product_images'] = response.xpath(PRODUCT_IMAGES_SRC_XPATH).getall() + response.xpath(
                ALTERNATE_PRODUCT_IMAGES_SRC_XPATH).getall()
            product_specs_elements = response.xpath(PRODUCT_SPECS_XPATH)
            if product_specs_elements:
                product_specs_elements = product_specs_elements[0]
                product_specs = {}
                for row in product_specs_elements.xpath('.//tr'):
                    key = row.xpath('.//td[1]//text()').get()
                    value = row.xpath('.//td[2]//text()').get()
                    product_specs[key] = value
                item['product_specs'] = product_specs

            company_description = response.xpath(COMPANY_DESCRIPTION_TEXT_XPATH).getall()
            item['company_description'] = "".join(company_description)

            product_category = "".join(response.xpath(PRODUCT_CATEGORY).getall()).replace('\xa0', " ")
            item['category'] = product_category


            with open(f"{self.file_name}", 'r+') as json_file:
                try:
                    json_file.seek(0)
                    current_data = json.load(json_file)
                except json.JSONDecodeError:
                    current_data = []
                data = dict(item)
                current_data.append(data)

                json_file.seek(0)
                json.dump(current_data, json_file, indent=4)

            yield item
        else:
            logger.info(f"STATUS: {response.status}")
