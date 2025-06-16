"""
Module combining the data scrapping from jdmart and jdmain, and further filteration of urls and records
"""
import re
from scrapy.crawler import CrawlerRunner
from twisted.internet import defer, reactor
from .vendor_details_spider import DetailSpider
from .jd_mart import main as jdmart_scraper
from .jd_main import main as jdmain_scraper
from libs.utils.constants import HEADERS, DOC_PATTERN, CITY_PATTERN, MATERIALS
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("justdial_data_scraper")


def remove_duplicate_urls_and_verify_city(url_list):
    """
    Removes duplicate URLs based on document IDs and verifies that the URLs belong to the city of Mumbai.

    This function processes a list of URLs, extracting document IDs from each URL using a regex pattern.
    It keeps track of seen document IDs to filter out duplicates. Only URLs containing the
    specified city pattern (Mumbai) are retained in the modified list.

    Args:
        url_list (list): A list of URLs to be processed.

    Returns:
        list: A list of unique URLs that contain the specified city p1rn.
    """
    pattern = DOC_PATTERN
    city_pattern = CITY_PATTERN
    seen_doc_ids = set()
    modified_url_list = []
    try:
        for url in url_list:
            doc_id = re.search(pattern, url)
            doc_id = doc_id.group(1)
            if doc_id not in seen_doc_ids:
                seen_doc_ids.add(doc_id)
                if re.search(city_pattern, url):
                    modified_url_list.append(url)
        return modified_url_list
    except Exception as e:
        logger.error(f"An error occurred in removing duplicate URLs: {str(e)}")
        return []


def main():
    """
    Main function for scraping data from JustDial.

    Args:
        materials (list): List of material names to be scraped.

    This function scrapes data from both JDMart and JDMain using the `jdmart_scraper` and
    `jdmain_scraper` functions respectively. It then combines the URLs from both sources,
    removes duplicates based on document IDs, and filters out URLs that do not belong to
    the city of Mumbai. Finally, it runs the `DetailSpider` for each material name,
    passing the filtered list of URLs as the start URLs.

    The function logs the number of URLs scraped from each source, the total number of
    URLs after combining both sources, the length after removing duplicates, and the
    length after filtering city.
    """
    runner = CrawlerRunner({"USER_AGENT": HEADERS["User-Agent"]})
    materials = MATERIALS
    try:
        @defer.inlineCallbacks
        def crawl_all():
            for material_name in materials:
                logger.info(f"Fetching data for {material_name}")
                urls_jdmart = jdmart_scraper(material=material_name)
                logger.info(
                    f"Scraped {len(urls_jdmart)} data from jdmart. Now scraping data from jdmain."
                )
                urls_jdmain = jdmain_scraper(material=material_name)
                logger.info(f"Scraped {len(urls_jdmain)} data from jdmain.")

                all_urls = urls_jdmain + urls_jdmart
                logger.info(f"Total length of URLs: {len(all_urls)}")

                # url_list after removing duplicates
                url_list = remove_duplicate_urls_and_verify_city(
                    urls_jdmain + urls_jdmart
                )
                logger.info(
                    f"Length after removing duplicates and filtering city: {len(url_list)}",
                )

                # Run the spider for the current category
                yield runner.crawl(
                    DetailSpider, start_urls=url_list, file_name=f"{material_name}.json"
                )

            reactor.stop()

        crawl_all()
        reactor.run()

    except Exception as e:
        logger.error(f"An error occurred in main scraping function: {str(e)}")
