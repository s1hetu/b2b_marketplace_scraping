"""
Script to scrape JD Mart for product details
"""
import tls_client
from .utils import (
    fetch_ajax_request,
    tweak_query_search_params,
    construct_url_for_request,
)
from libs.utils.config import JUSTDIAL_JDMART_URLS_OUTPUT_DIR_PATH
from libs.utils.constants import JUSTDIAL_BASE_URL
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("jd_mart")


def organize_data(entry):
    """
    Organizes the data from the scraped JDMart page into a dictionary
    that is easily accessible.

    Args:
        entry (list): A list of data scraped from JDMart page.

    Returns:
        dictionary: the organized dictionary
        str: the JD path.
    """
    try:
        organized_entry = {
            "ID": entry[0],
            "Business Name": entry[1],
            "City": entry[3],
            "Latitude": entry[4],
            "Longitude": entry[5],
            "Paid": entry[6],
            "Rating": entry[7],
            "Total Ratings": entry[8],
            "Phone Number": entry[16],
            "Image URL": entry[19],
            "Address": entry[64] if len(entry) > 64 else None,
            "Website URL": entry[36] if len(entry) > 36 else None,
            "JD path": entry[32],
            "Contract Info": (
                entry[87].get("contract_info")
                if len(entry) > 87 and entry[87]
                else None
            ),
            "Number of Enquiries": (
                entry[88][0].get("desc")
                if len(entry) > 88 and entry[88] and entry[88][0]
                else None
            ),
        }
        jd_url = JUSTDIAL_BASE_URL + entry[32]
        return organized_entry, jd_url
    except Exception as e:
        logger.error(f"An error occurred in organizing data: {str(e)}")
        return {}, ""


def format_page_response(response_data) -> tuple:
    """
    Formats the response data from a JDMart page scrape into a list of supplier data
    and a list of URLs.

    Args:
        response_data (dict): The response data from a JDMart page scrape.

    Returns:
        list: a list of supplier data and a list of URLs.
    """
    supplier_data_list = []
    url_list = []

    try:
        supplier_list_results = response_data["results"]
        supplier_list = supplier_list_results["data"]

        for supplier in supplier_list:
            supplier_data, website_url = organize_data(supplier)
            supplier_data_list.append(supplier_data)
            url_list.append(website_url)
        return supplier_data_list, url_list
    except Exception as e:
        logger.error(f"An error occurred in formatting page response: {str(e)}")
        return supplier_data_list, url_list


def export_data(filename, url_list):
    """
    Exports a list of URLs to a text file

    Args:
        filename (str): The filename to save the list of URLs to.
        url_list (list): The list of URLs to save.

    Returns:
        None
    """
    try:
        url_filename = f"{JUSTDIAL_JDMART_URLS_OUTPUT_DIR_PATH}/{filename}.txt"
        with open(url_filename, "w", encoding="utf-8") as f:
            for url in url_list:
                f.write(url + "\n")
        logger.info(f"URL list saved to '{url_filename}'.")
    except Exception as e:
        logger.error(f"An error occurred in exporting data to filename {filename}: {str(e)}")


def scrape_pages(api_request):
    """
    Scrapes pages from JustDial's JDMart using the Wrapi API.

    Args:
        api_request (requests.PreparedRequest): The request object containing the URL and headers.

    Returns:
        list: A list of URLs scraped from the pages.
    """
    logger.info("Attempting wrapi call")
    page_number = 1
    supplier_data = []
    url_list = []

    session = tls_client.Session(
        client_identifier="chrome112", random_tls_extension_order=True
    )

    try:
        while page_number < 15:
            logger.info(f"Page {page_number}")
            params = {"pg_no": page_number}
            url = tweak_query_search_params(api_request.url, params)
            response = session.post(
                url,
                headers=api_request.headers,
                data=api_request.body.decode("utf-8"),
            )

            if response.status_code == 200:
                response_data = response.json()
                formatted_response_data, suppliers_url_list = format_page_response(
                    response_data
                )
                supplier_data.extend(formatted_response_data)
                url_list.extend(suppliers_url_list)
            else:
                logger.error(f"STATUS CODE : {response.status_code}")
                continue

            page_number += 1
        return url_list
    except Exception as e:
        logger.error(f"An error occurred in scraping page {page_number}: {str(e)}")
        return url_list


def main(material):
    """
    Main function for scraping data from JDMart.

    Args:
        material (str): Material name to be scraped.

    Returns:
        list: List of URLs scraped from JDMart for the given material.
    """
    try:
        url = construct_url_for_request(material, city="Mumbai")
        api_request = fetch_ajax_request(url)
        url_list = scrape_pages(api_request)
        filename = material.replace(" ", "-")
        export_data(filename, url_list)
        return url_list
    except Exception as e:
        logger.error(f"An error occurred in JDMART scraping main function: {str(e)}")
        return []
