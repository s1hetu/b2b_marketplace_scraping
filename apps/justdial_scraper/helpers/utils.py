"""
Contains utility functions that are frequently used in the justdial scraper,
like making requests, setting up driver, etc.
"""
import time
from urllib.parse import urlparse
from seleniumwire import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import urllib
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from libs.utils.constants import HEADERS, WRAPI_URL_PATTERN, JUSTDIAL_BASE_URL
from libs.utils.log_services.logger import setup_logger
from libs.utils.config import PROXIES, HTTP_PROXY_VALUE

logger = setup_logger("jd_utils")

captured_request = False


def set_driver_options(headless: bool = True, scope: bool = False, proxies: bool = False):
    """
    Set up Chrome driver options, including user agent, maximize window, and add experimental options to avoid detection.
    Also, set up proxy if required.
    Params:
        headless: Whether to open browser in headless mode
        scope: Whether to scope the requests to WRAPI URL pattern
        proxies: Whether to use proxies
    Returns: The set-up driver
    """
    chrome_options = Options()
    user_agent = HEADERS["User-Agent"]
    chrome_options.add_argument(f"user-agent={user_agent}")
    chrome_options.add_argument("--start-maximized")
    selenium_wire_options = {}
    if headless:
        chrome_options.add_argument("--headless")
    if proxies:
        selenium_wire_options['proxy'] = {'http': HTTP_PROXY_VALUE}
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    service = Service(ChromeDriverManager().install())
    try:
        driver = webdriver.Chrome(
            options=chrome_options, service=service,
            seleniumwire_options=selenium_wire_options
        )

        if scope:
            driver.scopes = [WRAPI_URL_PATTERN]

        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        return driver
    except Exception as e:
        logger.error(f"An error occurred in setting/creating driver options: {str(e)}")
        return driver


def construct_url_for_request(product_name, city):
    """
    Construct the URL for making a request to JDMart with the given product_name and city
    Args:
        product_name (str): The product name to search for
        city (str): The city to search for
    Returns:
        str: The constructed URL
    """
    try:
        base_url = JUSTDIAL_BASE_URL
        search_product = product_name.replace(" ", "+")
        url = f"{base_url}/jdmart/{city}/{search_product}/suppliers"
        return url
    except Exception as e:
        logger.error(f"An error occurred in constructing URL: {str(e)}")
        return ""


def tweak_query_search_params(url, params):
    """
    Alter the search parameters of a given URL

    Args:
        url (str): The URL whose search parameters are to be altered
        params (dict): The new search parameters to be added/updated

    Returns:
        str: The updated URL with the new search parameters
    """
    try:
        url_parts = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qs(url_parts.query, keep_blank_values=True)
        query.update(params)
        updated_url = url_parts._replace(
            query=urllib.parse.urlencode(query, doseq=True)
        ).geturl()

        return updated_url
    except Exception as e:
        logger.error(f"An error occurred in altering search parameters: {str(e)}")
        return ""


def fetch_ajax_request(url):
    """
    Fetch the AJAX request for a given URL.

    Args:
        url (str): The URL whose AJAX request is to be fetched

    Returns:
        seleniumwire.Request: The AJAX request object
    """
    driver = set_driver_options(headless=True, scope=True, proxies=False)
    try:
        driver.get(url)
        logger.info(f"Opened URL: {url}")
        time.sleep(5)
        captured_requests = driver.requests
        for request in captured_requests:
            if not 'accounts.google.com' in request.url:
                wrapi_req = request
                break
        driver.quit()
        return wrapi_req
    except Exception as e:
        logger.error(f"An error occurred in capturing request: {str(e)} ")


def interceptor(request):
    """
    Intercepts a request and logs information about it, then assigns it to the captured_request global variable.

    Args:
        request (seleniumwire.Request): The request object to intercept

    Returns:
        None
    """
    logger.info("request intercepted")
    logger.info("request: ", request)
    logger.info("headers: ", request.headers)
    logger.info("payload: ", request.body.decode("utf-8"))
    logger.info("done")
    try:
        global captured_request
        captured_request = request
    except Exception as e:
        logger.error(f"An error occurred in intercepting request: {str(e)}")


def check_and_click_close_popup(driver):
    """Check for the close popup button and click it if found."""
    try:
        close_popup_button = WebDriverWait(driver, 0.05).until(
            EC.presence_of_element_located((By.CLASS_NAME, "jd_modal_close"))
        )
        if close_popup_button.is_displayed():
            try:
                close_popup_button.click()
                logger.info("Clicked 'jd_modal_close' button.")
                return True
            except Exception as e:
                logger.error("An error occurred in closing popup.")
    except Exception as e:
        logger.info("No closing popup found.")
    return False


def scroller_function(driver):
    """
    Scroll down the page until the end is reached or a request is captured.

    Args:
        driver (selenium.webdriver): The Selenium webdriver instance

    Returns:
        None
    """
    logger.info("Scrolling..")
    try:
        scroll_height = driver.execute_script("return document.body.scrollHeight")
        scroll_position_y = driver.execute_script(
            " return (window.innerHeight + Math.round(window.scrollY))"
        )
        global captured_request

        # footer_section = driver.find_element(By.XPATH, "//")
        while scroll_height > scroll_position_y and not captured_request:
            logger.info(
                f"scroll_height - {scroll_height}, scroll_position_y - {scroll_position_y}"
            )

            driver.execute_script("window.scrollBy(0,1000);")
            scroll_position_y = driver.execute_script(
                "return (window.innerHeight + Math.round(window.scrollY))"
            )
            check_and_click_close_popup(driver)
            time.sleep(4)
            new_scroll_height = driver.execute_script(
                "return document.body.scrollHeight"
            )
            scroll_height = new_scroll_height
        logger.info("scrolling complete")
    except Exception as e:
        logger.error(f"An error occurred in scrolling function: {str(e)}")
