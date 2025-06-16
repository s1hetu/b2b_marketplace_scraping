"""
Helpers for indiamart scraper
"""
from time import sleep
from selenium.common import TimeoutException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from seleniumwire import webdriver
from selenium.webdriver.support import expected_conditions as ec
from libs.utils.config import (
    HTTP_INDIAN_PROXY_VALUE, INDIAMART_SELENIUM_DRIVER_PATH)
from libs.utils.constants import (
    SCROLL_TO_END_SCRIPT, SCROLL_TO_TOP_SCRIPT)
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("indiamart_helpers")


class ScrapingHelpers:
    """
    Class for scraping data using selenium
    """

    @staticmethod
    def start_selenium_driver(
            use_chrome_profile: bool = True,
            use_incognito: bool = False,
            headless: bool = False,
            use_proxies: bool = False
    ):
        """
        Start the selenium driver with necessary conf
        :param use_chrome_profile: whether to use chrome profile
        :param use_incognito: whether to use incognito profile
        :param headless: whether to open browser in headless mode
        :param use_proxies: whether to use proxies
        :return: driver
        """
        try:
            chrome_service = Service(INDIAMART_SELENIUM_DRIVER_PATH)
            chrome_options = Options()
            selenium_wire_options = {}

            if use_chrome_profile:
                logger.info("Using chrome profile")
                chrome_options.add_argument('--user-data-dir=profiles/')
                chrome_options.add_argument('--profile-directory=Profile_7')
            if use_incognito:
                chrome_options.add_argument('--incognito')
            if headless:
                chrome_options.add_argument("--headless")
            if use_proxies:
                selenium_wire_options['proxy'] = {'http': HTTP_INDIAN_PROXY_VALUE}

            driver = webdriver.Chrome(
                options=chrome_options, service=chrome_service,
                seleniumwire_options=selenium_wire_options
            )
            driver.maximize_window()
            logger.info('\nDriver Started...\n')
        except Exception as e:
            logger.error(f"Error occurred while creating driver: {e}")
            driver = None
        return driver

    @staticmethod
    def load_whole_page(driver):
        """
        Load the page
        :param driver: driver instance
        """
        sleep(1.5)
        driver.execute_script(SCROLL_TO_END_SCRIPT)
        sleep(1)
        driver.execute_script(SCROLL_TO_END_SCRIPT)
        sleep(0.5)
        driver.execute_script(SCROLL_TO_TOP_SCRIPT)


scraping_helpers = ScrapingHelpers()


def fetch_element_by_xpath_with_wait(driver, seconds_to_wait: int, element_xpath: str, message: str = "details"):
    """
    Fetch the element by xpath with Webdriver wait
    :param driver: driver instance
    :param seconds_to_wait: Second to wait for an element
    :param element_xpath: The XPATH of the element
    :param message: Message to be displayed in case of error
    :return: element from web page
    """
    element = None
    try:
        element = WebDriverWait(driver, seconds_to_wait).until(
            ec.presence_of_element_located(
                (By.XPATH, element_xpath)))
    except TimeoutException:
        logger.error(f'Failed to fetch {message}.')
    except Exception as error:
        logger.error(f'Failed to fetch {message}. Unknown error occurred. ERROR: {str(error)}')
    return element


def fetch_elements_by_xpath_with_wait(driver, seconds_to_wait: int, element_xpath: str, message: str = "details"):
    """
    Fetch the elements by xpath with Webdriver wait
    :param driver: driver instance
    :param seconds_to_wait: Second to wait for an element
    :param element_xpath: The XPATH of the element
    :param message: Message to be displayed in case of error
    :return: element from web page
    """
    element = None
    try:
        element = WebDriverWait(driver, seconds_to_wait).until(
            ec.presence_of_all_elements_located(
                (By.XPATH, element_xpath)))
    except TimeoutException:
        logger.error(f'Failed to fetch {message}.')
    except Exception as error:
        logger.error(
            f'Failed to fetch {message}. Unknown error occurred: {str(error)}'
        )
    return element


def fetch_elements_by_xpath(driver, element_xpath: str, fetch_multiple: bool = False,
                            message: str = "details"):
    """
    Fetch the element by xpath
    :param driver: driver instance
    :param element_xpath: The XPATH of the element
    :param fetch_multiple: Whether to fetch multiple elements
    :param message: Message to be displayed in case of error
    :return: element from web page
    """
    elements = None
    try:
        elements = driver.find_elements(By.XPATH, element_xpath)
        if not fetch_multiple and len(elements) >= 1:
            elements = elements[0]
        if elements == []:
            elements = None
    except TimeoutException:
        logger.error(f'Failed to fetch {message}')
    except Exception as error:
        logger.error(
            f'Failed to fetch {message}. Unknown error occurred: {str(error)}'
        )
    return elements
