"""
Fetch company details
"""
import time
import json
from time import sleep
from selenium.common import ElementClickInterceptedException, ElementNotInteractableException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from libs.utils.config import INDIAMART_OUTPUT_DIR_PATH
from libs.utils.log_services.logger import setup_logger
from libs.utils.constants import (
    COMPANIES_SECTION_XPATH,
    COMPANY_CONTACT_NUMBER_XPATH,
    COMPANY_INFO_XPATH,
    COMPANY_REGION_XPATH, SHOW_MORE_RESULTS_XPATH, PRODUCT_INFO_XPATH, COMPANY_ADDRESS_XPATH)
from .helpers import scraping_helpers, fetch_elements_by_xpath, fetch_element_by_xpath_with_wait, \
    fetch_elements_by_xpath_with_wait

logger = setup_logger("indiamart_company_profile")


class IndiaMartScraper:
    """
    Class for scraping data from IndiaMart
    """
    driver = None
    search_query: str | None = None
    region: str | None = None
    company_section = None
    company_data = None

    def generate_url_from_inputs(self) -> str:
        """
        generate the URL from the search query and region
        :return: Generated URL
        """
        self.search_query.replace(' ', '+')
        generated_url = (f'https://dir.indiamart.com/search.mp?ss={self.search_query}&'
                         f'prdsrc=1&src=as-popular%7Ckwd%3D{self.search_query}%'
                         f'7Cpos%3D1%7Ccat%3D-2%7Cmcat%3D-2%7Ckwd_len%3D12%7Ckwd_cnt%3D2&c'
                         f'q={self.region}&com-cf=lw&res=RC5&stype=attr=1|attrS&Mspl=0&qry_typ=S'
                         f'&City={self.region.lower()}')

        logger.info(f"URL : {generated_url}")
        return generated_url

    def fetch_company_data(self) -> dict:
        """
        Fetch the company data
        :return: dictionary of company data
        """
        self.company_data = {
            'vendorId': None,
            'searchQuery': self.search_query,
            'regionSearchedFor': self.region,
            'companyName': None,
            'companyUrl': None,
            'companyRegion': None,
            'productUrl': None,
            'companyContactNumber': None,
            'company_address': None,
            'stars': None,
            'users_count': None
        }

        try:
            company_info = fetch_elements_by_xpath(driver=self.company_section,
                                                   element_xpath=COMPANY_INFO_XPATH,
                                                   fetch_multiple=False, message="company info")
            company_id = self.company_section.get_attribute("data-glid")
            self.company_data['vendorId'] = company_id
            if company_info:
                self.company_data['companyName'] = company_info.text
                self.company_data['companyUrl'] = company_info.get_attribute('href')

            company_region = fetch_elements_by_xpath(driver=self.company_section,
                                                     element_xpath=COMPANY_REGION_XPATH,
                                                     fetch_multiple=False, message="company region")
            if company_region:
                self.company_data['companyRegion'] = company_region.text

            product_info = fetch_elements_by_xpath(driver=self.company_section,
                                                   element_xpath=PRODUCT_INFO_XPATH,
                                                   fetch_multiple=False, message="product info")
            if product_info:
                self.company_data['productUrl'] = product_info.get_attribute('href')

            contact_number = fetch_elements_by_xpath(driver=self.company_section,
                                                     element_xpath=COMPANY_CONTACT_NUMBER_XPATH,
                                                     fetch_multiple=False,
                                                     message="contact number.")

            if contact_number:
                contact_number = contact_number.get_attribute(
                    'innerText')
                if len(contact_number) == 10:
                    self.company_data['companyContactNumber'] = contact_number
                else:
                    contact_number = contact_number.replace("+91 ", "")
                    alternate_numbers = []
                    if contact_number.startswith('0'):
                        contact_number = contact_number[1:]
                    actual_contact = contact_number[:10]
                    alternate_numbers.append(actual_contact)
                    extra_numbers = contact_number[10:].replace(",", "")
                    for i in range(len(extra_numbers) // 3):
                        alternate_number = actual_contact[:7] + extra_numbers[i:i + 3]
                        alternate_numbers.append(alternate_number)
                    self.company_data['companyContactNumber'] = alternate_numbers

            address = fetch_elements_by_xpath(driver=self.company_section,
                                              element_xpath=COMPANY_ADDRESS_XPATH,
                                              fetch_multiple=False, message="address")
            if address:
                self.company_data['company_address'] = address.get_attribute('innerText')

            ratings = fetch_elements_by_xpath(driver=self.company_section,
                                            element_xpath=".//span[@class='ratingValue']",
                                            fetch_multiple=False, message="ratings")
            if ratings:
                ratings_value = ratings.get_attribute('innerText')
                if ratings_value:
                    self.company_data['stars'] = ratings_value.split("/")[0]

            review_counts = fetch_elements_by_xpath(driver=self.company_section,
                                                    element_xpath=".//span[@class='color']",
                                                    fetch_multiple=False, message="reviews")
            if review_counts:
                reviews = review_counts.get_attribute('innerText')
                if reviews:
                    self.company_data['users_count'] = (reviews.replace("(", "").
                                                        replace(")", "").strip())

        except Exception as e:
            logger.error("Error:", e)
        return self.company_data

    def fetch_data_of_all_company_sections(
            self, company_sections: list
    ):
        """
        Fetch the data from company section
        :param company_sections: Elements of Company section
        :return: Data fetched from company section
        """
        companies_data = []
        for company_section in company_sections:
            try:
                present_classes = company_section.get_attribute('class')
                if (
                        'card   brs5 '
                        not in present_classes
                ):
                    continue
                self.company_section = company_section
                company_data = self.fetch_company_data()
                if company_data:
                    companies_data.append(company_data)
            except Exception as e:
                logger.error("Error while fetching data of company section", e)
        return companies_data

    def load_whole_page(self):
        """
        Load whole page.
        Scroll down upto specific height.
        Wait for button to be visible.
        Click the Show More Results button.
        Close pop-ups/adds.
        :return:
        """
        sleep(4)
        scroll_multiplier = 0.67
        return_scroll_height = "return document.body.scrollHeight;"

        next_page_button = fetch_element_by_xpath_with_wait(driver=self.driver, seconds_to_wait=10,
                                                            element_xpath=SHOW_MORE_RESULTS_XPATH,
                                                            message="next page button")
        if next_page_button:
            next_page_button_class = next_page_button.get_attribute('class')
            i = 1
            while (not next_page_button_class) and (i < 20):
                logger.info(f"{i} Iteration")
                try:
                    self.driver.execute_script(
                        "window.scrollTo(0, document.body.scrollHeight);"
                    )
                    sleep(3)
                    new_scroll_height = self.driver.execute_script(return_scroll_height)
                    updated_scroll_height = int(new_scroll_height * scroll_multiplier)
                    self.driver.execute_script(
                        f"window.scrollTo(0, {updated_scroll_height});"
                    )
                    sleep(2)
                    next_page_button = WebDriverWait(self.driver, 10).until(
                        ec.presence_of_element_located(
                            (By.XPATH, SHOW_MORE_RESULTS_XPATH)
                        )
                    )
                    next_page_button_class = next_page_button.get_attribute('class')
                    sleep(2)
                    next_page_button.click()
                    sleep(4)

                except (ElementClickInterceptedException, ElementNotInteractableException):
                    logger.error("Error while clicking show more results button to load more data.")
                    time.sleep(2)
                    ad_popup = WebDriverWait(self.driver, 10).until(
                        ec.presence_of_element_located(
                            (By.XPATH, "//*[@id='t0901_cls']")
                        )
                    )
                    logger.info(f"Add pop up text - {ad_popup.text}")
                    if ad_popup.text == 'X':
                        logger.info("closing popup")
                        ad_popup.click()
                    time.sleep(2)
                    scroll_multiplier = 0.93
                    new_scroll_height = self.driver.execute_script(return_scroll_height)
                    updated_scroll_height = int(new_scroll_height * scroll_multiplier)
                    self.driver.execute_script(
                        f"window.scrollTo(0, {updated_scroll_height});"
                    )
                    next_page_button = WebDriverWait(self.driver, 10).until(
                        ec.presence_of_element_located(
                            (By.XPATH, SHOW_MORE_RESULTS_XPATH)
                        )
                    )
                    next_page_button_class = next_page_button.get_attribute('class')

                except Exception:
                    logger.error(
                        "Exception while clicking or fetching show more "
                        "results button to load more pages.")
                    new_scroll_height = self.driver.execute_script(return_scroll_height)
                    updated_scroll_height = int(new_scroll_height * scroll_multiplier)
                    self.driver.execute_script(
                        f"window.scrollTo(0, {updated_scroll_height});"
                    )
                    self.driver.execute_script("window.scrollTo(0, 0);")
                i += 1
        else:
            logger.info("Unable to find button.")

    def scarp_indiamart_by_search_query_with_selenium(self,
                                                      search_query: str,
                                                      region: str,
                                                      file_name: str,
                                                      headless: bool = False,
                                                      use_proxies: bool = False
                                                      ):
        """
        Open the selenium Chrome browser, load page and get data
        :param search_query: The query to be searched
        :param region: The region for the search query
        :param file_name: The name of the file to save data
        :param headless: Whether to use headless mode
        :param use_proxies: Whether to use proxies
        :return: Message and JSON file with data
        """
        file_name = file_name.replace(" ", "-")
        json_file_name = f"{INDIAMART_OUTPUT_DIR_PATH}/{file_name}.json"
        try:
            """start selenium driver"""
            self.driver = scraping_helpers.start_selenium_driver(
                use_chrome_profile=True, use_incognito=False,
                headless=headless, use_proxies=use_proxies
            )

            if not self.driver:
                message = "Unable to create driver"
                return message, None
            self.search_query = search_query
            self.region = region
            url = self.generate_url_from_inputs()
            self.driver.get(url)

            logger.info(f'Url for search query: {search_query} and region: {region} opened.\n')

            """ load whole page """
            self.load_whole_page()
            logger.info("Page loaded.")

            company_sections = fetch_elements_by_xpath_with_wait(
                driver=self.driver,
                seconds_to_wait=10,
                element_xpath=COMPANIES_SECTION_XPATH)
            if company_sections:
                logger.info(
                    f'Total {len(company_sections)} company sections '
                    f'found in this page. Fetching data from opened page...\n'
                )

                companies_data = self.fetch_data_of_all_company_sections(company_sections)
                if companies_data:
                    logger.info("Company data fetched. Now fetching metadata.")
                    message = (f'Successfully scraped data of search query: '
                               f'{search_query} for region: {region}.')
                else:
                    message = "Unable to find companies data."
                    logger.info("Unable to find companies data.")
                    companies_data = []

                with open(json_file_name, 'w', encoding="utf-8") as json_file:
                    json.dump(companies_data, json_file)
                    logger.info(f"JSON File : {json_file_name}")
                self.driver.quit()
            else:
                message = "Unable to find company sections"
                logger.info("Unable to find company sections")
        except Exception as error:
            logger.error(f"Error: {error}")
            message = (f'Failed to scraped data for  search query: '
                       f'{search_query} for region: {region}.')
        return message, json_file_name
