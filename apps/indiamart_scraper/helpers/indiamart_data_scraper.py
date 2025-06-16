"""
Scraper to visit URL via Selenium
"""
import json
from scrapy.crawler import CrawlerRunner
from twisted.internet import defer, reactor
from .company_profile import IndiaMartScraper
from .product_url_scraping import ProductScraper
from libs.utils.constants import MATERIALS, USER_AGENT
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("indiamart_data_scraper")


def scrap_product_url(file_name: str) -> tuple:
    """
    Get the list of companies_with_product_urls and companies_without_product_urls from the JSON file.
    :param file_name: Name of the file where data is loaded.
    :return: tuple of lists of companies_with_product_urls companies_without_product_urls
    """
    companies_with_product_urls = []
    companies_without_product_urls = []
    try:
        with open(file_name, 'r', encoding="utf-8") as json_file:
            data = json.load(json_file)

        for company in data:
            if company.get('productUrl'):
                companies_with_product_urls.append(company)
            else:
                companies_without_product_urls.append(company)
    except Exception as e:
        logger.error(f"Unable to bifurcate data based on productUrl - {e}")

    return companies_with_product_urls, companies_without_product_urls


def main():
    """
    Main entry point for scraping data from IndiaMart.
    For each category
        It opens the selenium chrome browser, and performs clicks + scroll.
        Once the page is completely scrolled, and there is no more data to load, it save data to JSON file and quits the chrome browser.
        Then it bifurcates the data based on product url, and passes list of companies having product url to Scrapy and saves data to JSON file.

    """
    india_mart_scraper = IndiaMartScraper()
    runner = CrawlerRunner({'USER_AGENT': USER_AGENT})
    all_categories_list = MATERIALS
    region = "Mumbai"

    @defer.inlineCallbacks
    def crawl_all():
        for category in all_categories_list:
            try:
                message, file = india_mart_scraper.scarp_indiamart_by_search_query_with_selenium(
                    search_query=category,
                    region=region,
                    file_name=category,
                    headless=True,
                    use_proxies=True
                )
                if file:
                    companies_with_product_url, companies_without_product_url = scrap_product_url(file)
                    with open(file, 'w', encoding="utf-8") as output_file:
                        if companies_without_product_url:
                            json.dump(companies_without_product_url, output_file)

                    # Run the spider for the current category
                    yield runner.crawl(
                        ProductScraper,
                        file_name=file,
                        extra_data=companies_with_product_url
                    )

                else:
                    logger.info(f"Message: {message}")

            except Exception as e:
                logger.error(f"Exception has occurred - {e}")
        reactor.stop()

    crawl_all()
    reactor.run()
