"""
Fetch the GST details and the return details of the unique GSTs fetched from data.
To run the file: python3 -m libs.utils.gst_extractor.gst_details_extractor
"""
import json
import requests
from database import db
from libs.utils.constants import USER_AGENT, GST_BASE_URL, GST_RETURNS_BASE_URL
from libs.utils.config import GST_DIR_PATH, GST_API_KEY, RETURNS_API_KEY, \
    RAW_SCRAPED_DATA_COLLECTION
from libs.utils.log_services.logger import setup_logger

logger = setup_logger("gst-details-extractor")


def fetch_unique_gsts():
    """
    Fetch unique GSTs from combined data. Reads the combined data JSONs and fetches the unique GSTs.
    Args: 
        None
    Returns:
        unique_gsts: list of unique GSTs.
    """
    companies_with_gst = (db.get_or_create_collection(RAW_SCRAPED_DATA_COLLECTION).find
                          ({"gst": {"$ne": None}},
                           {"_id": 0, "gst": 1})).to_list()
    logger.info(f"{len(companies_with_gst)} Unique GSTs Fetched..")
    unique_gst_list = list(set(company['gst'] for company in companies_with_gst))
    if len(companies_with_gst) != len(unique_gst_list):
        logger.info(f"Found {len(companies_with_gst) - len(unique_gst_list)} duplicate GSTs.")
    return unique_gst_list


def fetch_gst_details(gst, headers):
    """
    Fetch gst details for given gst number with a retry mechanism of 3 times.
    :param gst: The gst number for which details need to be fetched.
    :param headers: The headers for requesting the API
    :return: GST details received from API.
    """
    gst_data = {}
    for _ in range(3):
        try:
            response = requests.get(f'{GST_BASE_URL}/{GST_API_KEY}/{gst}',
                                    headers=headers, timeout=100)
            if response.status_code == 200:
                gst_response_data = response.json()
                gst_data = gst_response_data.get('data')

                # to get certain required fields only from the API response,
                # follow the below structure
                # {
                #     'lastUpdated': data['lstupdt'],
                #     'status': data['sts'],
                #     'legalName': data['lgnm'],
                #     'tradeName': data['tradeNam'],
                #     'primaryAddress': data['pradr'],
                #     'taxpayerType': data['dty'],
                #     'registrationDate': data['rgdt'],
                #     'natureOfBusiness': data['nba'],
                #     'natureOfTaxpayer': data['ntcrbs']
                # }
                if gst_data:
                    logger.info(f"GST Details fetched for {gst}")
                    break
                else:
                    logger.info(f"GST Details not found for {gst}")
            else:
                logger.info(f"Received Status code : {response.status_code} "
                            f"while fetching GST data for {gst}")
        except Exception as error:
            logger.error(f"Could not fetch GST details for {gst}, error: {error}")
    else:
        logger.info(f"Tried fetching GST details for {gst}, but unable to get response.")
    return gst_data


def fetch_return_details(gst, headers):
    """
        Fetch gst return details for given gst number with a retry mechanism of 3 times.
        :param gst: The gst number for which details need to be fetched.
        :param headers: The headers for requesting the API
        :return: GST return details received from API.
        """
    filing_status_data = []
    for _ in range(3):
        try:
            gst_return_response = requests.get(f'{GST_RETURNS_BASE_URL}/'
                                               f'{RETURNS_API_KEY}/{gst}',
                                               headers=headers, timeout=100)
            if gst_return_response.status_code == 200:
                gst_return_data = gst_return_response.json()
                return_data = gst_return_data.get('data')
                if return_data:
                    filing_data = return_data.get('filingStatus')
                    if filing_data and isinstance(filing_data, list):
                        if len(filing_data) >= 1:
                            filing_status_data = filing_data[0]
                            logger.info(f"Return Data fetched for {gst}")
                        else:
                            logger.info(f"No Return filing status details available for {gst}.")
                        break
                    else:
                        logger.info(f"Unable to fetch filing status data for {gst}")
                else:
                    logger.info(f"Unable to fetch return details for {gst}")
            else:
                logger.info(
                    f"Received Status code : {gst_return_response.status_code} while "
                    f"fetching GST Return data for {gst}")
        except Exception as error:
            logger.error(f"Could not fetch Return Details for {gst}, error: {error}")
    else:
        logger.info(f"Tried fetching GST details for {gst}, but unable to get response.")
    return filing_status_data


def fetch_gst_data(unique_gsts):
    """
    Fetch GST details and return data for the given list of unique GSTs and store in a JSON file

    Args:
        unique_gsts (list): List of unique GSTs.

    Returns:
        None
    """
    headers = {
        "User-Agent": USER_AGENT
    }
    gst_details_list = []
    for gst in unique_gsts:
        try:
            gst_details = fetch_gst_details(gst, headers)
            return_details = fetch_return_details(gst, headers)
            gst_details_data = {
                "gst": gst,
                "gst_details": gst_details,
                "return_details": return_details
            }
            gst_details_list.append(gst_details_data)
        except Exception as error:
            logger.error(f"Skipped appending for {gst} - {str(error)}")

    logger.info(f"The length of GST details list is: {len(gst_details_list)}")

    try:
        with open(f"{GST_DIR_PATH}/gst_details_data.json", "w", encoding="utf-8") as f:
            json.dump(gst_details_list, f, ensure_ascii=False, indent=4)
        logger.info(f"Successfully dumped data into file: {GST_DIR_PATH}/gst_details_data.json")
    except Exception as error:
        logger.error(f"Error in writing to file: {str(error)}")
        with open(f"{GST_DIR_PATH}/gst_details_data.txt", "w", encoding="utf-8") as f:
            f.write(str(gst_details_list))


def main():
    """
    Main function to fetch gst details and return details
    """
    unique_gsts = fetch_unique_gsts()
    fetch_gst_data(unique_gsts)
