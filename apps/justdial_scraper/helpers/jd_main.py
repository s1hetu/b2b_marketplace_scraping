"""
Script containing code to scrape JD Main website to collect vendor details
"""
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .utils import scroller_function, set_driver_options
from libs.utils.config import JUSTDIAL_JDMAIN_URLS_OUTPUT_DIR_PATH
from libs.utils.constants import JUSTDIAL_BASE_URL, PARENT_DIV_XPATH, URL_DIV_XPATH, MAY_BE_LATER_CLASS_NAME
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("jd_main")


def close_login_popup(driver):
    """
    Closes the 'Maybe Later' popup if it appears.
    The popup asks user to login/signup to JD Main website.
    """
    try:
        # Check for 'Maybe Later' popup and click it if found
        maybe_later_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, MAY_BE_LATER_CLASS_NAME))
        )
        if maybe_later_button.is_displayed():
            try:
                maybe_later_button.click()
                logger.info("Clicked 'Maybe Later' button.")
            except Exception as e:
                logger.error("Maybe Later popup not found or failed to click")
    except Exception as e:
        logger.error("Maybe Later popup not found.")


def parse_data(driver):
    """
    Parse the vendor details page and extract the URLs of the vendors.

    Args:
        driver (selenium.webdriver): The Selenium WebDriver instance.

    Returns:
        list: A list of URLs of the vendors on the page.
    """
    url_list = []
    try:
        parent_divs = driver.find_elements(By.CLASS_NAME, PARENT_DIV_XPATH)
        if not parent_divs:
            logger.info("No parent divs found. Check the class name and page source.")
        else:
            for index, parent_div in enumerate(parent_divs):
                try:
                    url_div = parent_div.find_element(
                        By.CLASS_NAME, URL_DIV_XPATH
                    )
                    url = url_div.get_attribute("href")
                    url_list.append(url)
                except Exception as e:
                    logger.error(f"An error occurred in parent div {index}\n")
    except Exception as e:
        logger.error(f"An error occurred in parsing data: {str(e)}")
    return url_list


def write_data(driver, url):
    """
    Writes the scraped URLs from the given page to a text file.

    Args:
        driver (selenium.webdriver): The Selenium WebDriver instance.
        url (str): The URL of the page being scraped.

    Returns:
        list: A list of URLs scraped from the page.
    """
    try:
        url_filename = (
            f"{JUSTDIAL_JDMAIN_URLS_OUTPUT_DIR_PATH}/{url.split('/')[-1]}.txt"
        )
        supplier_url_list = parse_data(driver)

        with open(url_filename, "w", encoding="utf-8") as f:
            if supplier_url_list:
                for supplier_url in supplier_url_list:
                    f.write(supplier_url + "\n")
                logger.info(f"URL list saved to '{url_filename}'.")
            else:
                logger.info("No urls found in jdmain.")
        return supplier_url_list
    except Exception as e:
        logger.error(f"An error occurred in writing data: {str(e)}")
        return []


def main_scraper(url):
    """
    Scrapes the given URL and writes the scraped URLs to a text file.

    Args:
        url (str): The URL of the page to be scraped.

    Returns:
        list: A list of URLs scraped from the page.
    """
    try:
        driver = set_driver_options(headless=True, scope=False, proxies=True)
        logger.info("Created driver.")
        driver.get(url)
        logger.info(f"Opened URL: {url}")
        close_login_popup(driver)
        scroller_function(driver)
        url_list = write_data(driver, url)
        driver.quit()
        return url_list

    except Exception as e:
        logger.error(f"An error occurred in main scraper: {str(e)}")
        return []
    finally:
        driver.quit()


def construct_url(material, city):
    """
    Constructs a URL for scraping vendor details from JD Main.

    Args:
        material (str): The name of the material to search for.
        city (str): The city where the search will be conducted.

    Returns:
        str: The constructed URL for the given material and city.
    """
    try:
        base_url = JUSTDIAL_BASE_URL
        material_query = material.replace(" ", "-")
        return f"{base_url}/{city}/{material_query}"
    except Exception as e:
        logger.error(f"An error occurred in constructing URL:{str(e)}")
        return ""


def main(material):
    """
    Main function to scrape vendor URLs from JD Main.

    Args:
        material (str): The name of the material for which vendor details are to be scraped.

    Returns:
        list: A list of vendor URLs for the given material.
    """
    try:
        url = construct_url(material, city="Mumbai")
        url_list = main_scraper(url)
        return url_list
    except Exception as e:
        logger.error(f"An error occurred in main function: {str(e)}")
        return []
