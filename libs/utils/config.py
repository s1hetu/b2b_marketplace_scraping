"""
Configs for apps
"""
import os
from dotenv import dotenv_values

ENV_PATH = '.env'

if not os.path.exists(ENV_PATH):
    raise Exception('.env file not found')

config = dotenv_values(ENV_PATH)

OUTPUT_DIR = config.get('OUTPUT_DIR_PATH', 'output')
os.makedirs(OUTPUT_DIR, exist_ok=True)

COMBINED_DATA_DIR=config.get('COMBINED_DATA_DIR', 'categories')
COMBINED_DATA_DIR_PATH = os.path.join(os.getcwd(), OUTPUT_DIR, COMBINED_DATA_DIR)
os.makedirs(COMBINED_DATA_DIR_PATH, exist_ok=True)

FLASK_HEADERS = [
    "Origin",
    "X-Requested-With",
    "Content-Type",
    "Accept",
    "Authorization",
    "Access-Control-Allow-Origin",
]

HTTP_PROXY_VALUE = config.get('HTTP_PROXY_VALUE')
HTTPS_PROXY_VALUE = config.get('HTTPS_PROXY_VALUE')

PROXIES = {
    'http': HTTP_PROXY_VALUE,
    'https': HTTPS_PROXY_VALUE
}


# Configs for deldure scraper

DELDURE_PORT = int(config.get("DELDURE_PORT"))

DELDURE_DIR = config.get('DELDURE_OUTPUT_DIR_PATH', 'deldure')
DELDURE_OUTPUT_DIR_PATH = os.path.join(os.getcwd(), OUTPUT_DIR, DELDURE_DIR)
os.makedirs(DELDURE_OUTPUT_DIR_PATH, exist_ok=True)

DELDURE_VENDOR_URLS_DIR = config.get('DELDURE_VENDOR_URLS_DIR', 'vendor_urls')
DELDURE_VENDOR_URLS_DIR_PATH = os.path.join(DELDURE_OUTPUT_DIR_PATH, DELDURE_VENDOR_URLS_DIR)
os.makedirs(DELDURE_VENDOR_URLS_DIR_PATH, exist_ok=True)


# Configs for indiamart scraper

INDIAMART_PORT = int(config.get("INDIAMART_PORT"))

INDIAMART_DIR = config.get('INDIAMART_OUTPUT_DIR_PATH', 'indiamart')
INDIAMART_OUTPUT_DIR_PATH = os.path.join(os.getcwd(), OUTPUT_DIR, INDIAMART_DIR)
os.makedirs(INDIAMART_OUTPUT_DIR_PATH, exist_ok=True)

INDIAMART_SELENIUM_DRIVER_PATH = config.get('INDIAMART_SELENIUM_DRIVER_PATH')
INDIAMART_CHROME_PROFILE_PATH = config.get('INDIAMART_CHROME_PROFILE_PATH')

HTTP_INDIAN_PROXY_VALUE = config.get('HTTP_INDIAN_PROXY_VALUE')

MAX_COMPANY_METADATA_REQUEST_RETRY = config.get(
    'MAX_COMPANY_METADATA_REQUEST_RETRY', 5
)

INDIAMART_SCRAPER_CUSTOM_SETTINGS = {
    'HTTPPROXY_ENABLED': True
}


# Configs for justdial scraper

JUSTDIAL_PORT = int(config.get("JUSTDIAL_PORT"))

JUSTDIAL_DIR=config.get('JUSTDIAL_OUTPUT_DIR_PATH', 'justdial')
JUSTDIAL_OUTPUT_DIR_PATH = os.path.join(os.getcwd(), OUTPUT_DIR, JUSTDIAL_DIR)
os.makedirs(JUSTDIAL_OUTPUT_DIR_PATH, exist_ok=True)

JUSTDIAL_JDMART_URLS_OUTPUT_DIR_PATH = os.path.join(
    JUSTDIAL_OUTPUT_DIR_PATH, config.get("JUSTDIAL_JDMART_URLS_OUTPUT_DIR_PATH", "urls/jdmart"))
os.makedirs(JUSTDIAL_JDMART_URLS_OUTPUT_DIR_PATH, exist_ok=True)

JUSTDIAL_JDMAIN_URLS_OUTPUT_DIR_PATH = os.path.join(
    JUSTDIAL_OUTPUT_DIR_PATH, config.get("JUSTDIAL_JDMAIN_URLS_OUTPUT_DIR_PATH", "urls/jdmain"))
os.makedirs(JUSTDIAL_JDMAIN_URLS_OUTPUT_DIR_PATH, exist_ok=True)

#Configs for google business data
GOOGLE_BUSINESS_DATA_PORT = int(config.get("GOOGLE_BUSINESS_DATA_PORT"))

# Configs for DB
DB_URL = config.get("DB_URL", "mongodb://localhost:27017/")
DB_NAME = config.get("DB_NAME", "ij")
RAW_SCRAPED_DATA_COLLECTION = config.get("RAW_SCRAPED_DATA_COLLECTION", "raw-sellers")
GST_DATA_COLLECTION = config.get("GST_DATA_COLLECTION", "gst-details")
GOOGLE_BUSINESS_DATA_COLLECTION = config.get("GOOGLE_BUSINESS_DATA_COLLECTION", "google-business-data")

#GSTs
GST_DIR = config.get('GST_DIR', 'gst_details')
GST_DIR_PATH = os.path.join(os.getcwd(), GST_DIR)
os.makedirs(GST_DIR_PATH, exist_ok=True)
GST_API_KEY=config.get('GST_API_KEY')
RETURNS_API_KEY=config.get("RETURNS_API_KEY")

GOOGLE_BUSINESS_DATA_DIR = config.get('GOOGLE_BUSINESS_DATA_DIR', 'gbd')
GOOGLE_BUSINESS_DATA_DIR_PATH = os.path.join(os.getcwd(), GOOGLE_BUSINESS_DATA_DIR)
os.makedirs(GOOGLE_BUSINESS_DATA_DIR_PATH, exist_ok=True)
X_RAPIDAPI_KEY=config.get('X_RAPIDAPI_KEY')
X_RAPIDAPI_HOST=config.get('X_RAPIDAPI_HOST')
