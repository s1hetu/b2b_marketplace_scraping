"""
Request the Deldure for categories and fetch vendor IDs to pass URLS to Scrapy.
"""
import os
import ast
import requests
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
import urllib3.exceptions
from requests.exceptions import RetryError
from twisted.internet import reactor, defer
from scrapy.crawler import CrawlerRunner
from dotenv import load_dotenv
from libs.utils.log_services.logger import setup_logger
from libs.utils.config import PROXIES, DELDURE_VENDOR_URLS_DIR_PATH
from .vendor_details import VendorDetailsSpider
from libs.utils.constants import (
    HEADERS,
    COOKIES,
    MATERIALS,
    VENDOR_LIST_URL,
    VENDOR_DETAILS_URL,
)

load_dotenv()
logger = setup_logger("deldure_vendor_list")

# Define the initial parameters
params = {
    "query": "jcb",
    "page": 1,
    "state": "Maharashtra",
    "city": "Mumbai",
    "country": "India",
}

proxies = PROXIES


# Function to fetch data from search pages
def create_connection():
    """
    Creates a requests session with a retry strategy and proxy settings.

    Returns:
        requests.Session
    """

    retry_strategy = Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"],
        backoff_factor=3,
    )

    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.proxies = proxies
    http.mount("https://", adapter)
    http.mount("http://", adapter)
    return http


def scrape_data(params):
    """
    Fetches vendor data from Deldure by scraping search pages.

    Args:
        params (dict): Parameters to be passed with the request.
    Returns:
        tuple: Contains a list of vendor URLs and the category name.
    """
    page = params.get("page")
    http = create_connection()

    vendor_list = []
    while page <= 50:
        logger.info(f"Fetching page {page} data...")
        try:
            response = http.get(
                VENDOR_LIST_URL,
                params=params,
                headers=HEADERS,
                proxies=proxies,
                cookies=COOKIES,
            )

            if response.status_code == 200:
                data = response.json()
                vendor_list.extend(data.get("directorySearchList", []))
                logger.info(f"Page {page} fetched successfully.")
            else:
                logger.error(
                    f"Failed to fetch page {page}, status code: {response.status_code}"
                )

        except (urllib3.exceptions.MaxRetryError, urllib3.exceptions.ResponseError):
            logger.error(
                f"RetryError Unable to collect page {page} data response {response.status_code}"
            )
            break
        except RetryError as e:
            logger.error(
                f"RetryError Unable to collect page {page} data response {response.status_code}"
            )
            http.close()
            http = create_connection()
            break
        except Exception as e:
            logger.error(
                f"Ran into error while collecting page {page} data. ERROR: {str(e)}"
            )
        page += 1
        params["page"] = page

    logger.info(f"Number of vendors found: {len(vendor_list)}")

    try:
        category_name = params.get("query").replace(" ", "-")
        file_path = f"{DELDURE_VENDOR_URLS_DIR_PATH}/{category_name}.txt"
        urls = []

        with open(file_path, "a") as file:
            for vendor in vendor_list:
                vendor_id = vendor.get("id")
                if vendor_id:
                    vendor_url = f"{VENDOR_DETAILS_URL}/{vendor_id}"
                    file.write(vendor_url + "\n")
                    urls.append(vendor_url)
                    logger.info(f"Added vendor ID {vendor_id} to URL list")

        return urls, category_name

    except Exception as e:
        logger.error(f"Error occurred while processing vendor details: {e}")
        return [], None


def run_scrapy(urls, material):
    """
    Run Scrapy to fetch vendor details using the given list of URLs and material.

    Args:
        urls : List of URLs to fetch vendor details from.
        material : Material name to be used for saving the scraped data.

    Returns:
        Deferred:object that resolves when the crawl is finished.
    """
    runner = CrawlerRunner()
    return runner.crawl(VendorDetailsSpider, urls=urls, material=material)


@defer.inlineCallbacks
def run_all_spiders(material_list):
    """
    Runs all spiders in sequence, one for each material in the given list.

    Args:
        material_list (list): List of material names to be used for scraping vendor details.

    Yields:
        Deferred: object that resolves when all spiders have finished.
    """
    for material in material_list:
        params["query"] = material
        params["page"] = 1  # Reset page to 1 for each material search
        urls, category_name = scrape_data(params)  # Fetch vendor URLs

        if urls:
            yield run_scrapy(urls, category_name)
    reactor.stop()


def main():
    """
    Main entry point for the vendor list scraper.

    Starts the Twisted reactor and runs all spiders in sequence, one for each material in the given list.

    Args:
        None

    Returns:
        None
    """
    material_list = MATERIALS

    runner = CrawlerRunner()
    run_all_spiders(material_list)
    reactor.run()
