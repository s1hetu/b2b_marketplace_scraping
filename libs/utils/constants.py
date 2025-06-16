"""
Constants for apps
"""

MATERIALS = [
    "Aggregates",
    "Aluminium",
    "Backhoe",
    "Beams",
    "Binding Wires",
    "Boring Machine",
    "Bricks",
    "Bulldozer",
    "Cement",
    "Chisels",
    "Concrete",
    "Concrete Mixers",
    "Conveyors",
    "Core cutter machine",
    "Cranes",
    "Crushers",
    "Disc Grinder",
    "Drill Rig",
    "Drilling Machine",
    "Dumper Trucks",
    "Excavator",
    "Glass",
    "Granite",
    "Hammer",
    "JCB",
    "Limestone",
    "Measuring Tapes",
    "Pipe Layer",
    "Plastic",
    "Road Roller",
    "Rubber Boots",
    "Sand",
    "Sand Screening Machine",
    "Saw",
    "Shield Helmet",
    "Steel",
    "Stone",
    "Tiles",
    "Trucks",
    "Wood",
    "Wooden Float",
]

DATA_COMPARISON_DICT = {
    'Deldure': ['phone', 'website', 'email'],
    'IndiaMart': ['phone', 'website'],
    'JustDial': ['phone', 'website', 'email']
}

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) Gecko/20100101 Firefox/98.0"

# Constants for deldure scraper
HEADERS = {
    "User-Agent": USER_AGENT,
    "accept": "*/*",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
    "apikey": "a13c17f7-c898-5c74-c0e2-3ba04ca942c6",
    "referer": "https://www.deldure.com/",
}
COOKIES = {
    "_ga": "GA1.1.1435931814.1730803468",
    "JSESSIONID": "5TPGJfUHQ8_7OHL4mfMVr3u0Y6t3w8qWHrfLyMyF.localhost",
    "__gads": "ID=d2642c24b766d299:T=1730803471:RT=1730886985:S=ALNI_MbGxF8_Ol3_5VK8k_S4k1NjIyOqJQ",
    "__gpi": "UID=00000f60e883f1df:T=1730803471:RT=1730886985:S=ALNI_MaJV3Wmbv4zPM4K7xmIBV8AFg3aPQ",
    "__eoi": "ID=32aed1f573fb915b:T=1730803471:RT=1730886985:S=AA-AfjbAe3H7JXi-rBuTMCSYGQ_6",
    "_ga_P7F0083FXY": "GS1.1.1730883968.4.1.1730887027.15.0.1335140404",
    "FCNEC": "%5B%5B%22AKsRol-nsR8ZPXRMI8m_hstUG6gxeMcbnqayvvvoBIL_uVjg_BQEPuKfG0j8oFtH5wYetFP6yfD3xb0PC1DFpSkWhDqoWcXmxPgLiH7MKqa8U7pnyVVnTp2OvAfmetoQLjOXzenHjmRZ65DqaoxBcT7VZkxZ-Kj7sA%3D%3D%22%5D%5D",
}
DELDURE_SCRAPY_CUSTOM_SETTINGS = {
    "DOWNLOAD_DELAY": 1,
    "RETRY_ENABLED": True,
    "RETRY_TIMES": 3,
}

VENDOR_LIST_URL = "https://www.deldure.com/api/v1/search"
VENDOR_DETAILS_URL = "https://www.deldure.com/api/v1/vendor"

# Constants for indiamart scraper

# XPATH
SCROLL_TO_END_SCRIPT = 'window.scrollTo(0, document.body.scrollHeight);'
SCROLL_TO_TOP_SCRIPT = 'window.scrollTo(0, 0);'
SHOW_MORE_RESULTS_XPATH = "//div[@class='showmoreresultsdiv']/button"
COMPANIES_SECTION_XPATH = "//div[@class='listingCardContainer']/div[@class='card   brs5 ']"
COMPANY_INFO_XPATH = './div[@class="cardbody"]/div[@class="companyname "]/a[@class="cardlinks"]'
PRODUCT_INFO_XPATH = ('./div[@class="cardbody"]/div[@class="titleAskPriceImageNavigation"]/'
                      'div/span/a[@class="cardlinks"]')
CLICK_ON_VIEW_NUMBER_XPATH = './/span[@class="mo viewn vmn fs14 clr5 fwb view_mob"]'
COMPANY_REGION_XPATH = './/span[@class="elps elps1"]'
COMPANY_SECTION_CHILDREN_XPATH = './/div[@class="cardbody"]/div'
COMPANY_CONTACT_NUMBER_XPATH = './/span[@class="pns_h duet fwb"]'
GST_NO_XPATH = './/span[@class="FM_bo"]'
VERIFIED_TAG_XPATH = './/p[@class="FM_trs FM_ds15 FM_ds5 FM_Lsp"]'
LIST_FIELDS_XPATH = './/div[@class="FM_ds5 FM_ds6 FM_ds9 FM_ds13"]'
FIELD_HEADING_XPATH = '//p[@class="FM_c6 FM_f15 FM_m13"]'
FIELD_VALUE_XPATH = '//div.//span[@class="Fm_lh18 FM_f16 FM_c1"]'
RATINGS_XPATH = '//div[@id="slr_rtng"]'
STARS_XPATH = './/span[@class="bo color"]'
STARS_TEXT_XPATH = './/span[@class="bo color"]/text()'
USERS_COUNT_XPATH = './/span[@class="tcund"]'
USERS_COUNT_TEXT_XPATH = './/span[@class="tcund"]/text()'
VERIFIER_NAME_XPATH = './/span[@class="lh11"]'
VERIFIER_NAME_TEXT_XPATH = './/span[@class="lh11"]/text()'
CALL_RESPONSE_RATE_XPATH = './/span[@class="lh11 fs11 on color1 mt5"]'
CALL_RESPONSE_RATE_TEXT_XPATH = './/span[@class="lh11 fs11 on color1 mt5"]/text()'
PRODUCT_IMAGES_XPATH = '//div[@class="tn9_card pcp"]'
PRODUCT_IMAGES_SRC_XPATH = '//div[@class="tn9_card pcp"]/img/@src'
ALTERNATE_PRODUCT_IMAGES = '//div[@class="slider sthum"]/div'
ALTERNATE_PRODUCT_IMAGES_SRC_XPATH = '//div[@class="slider sthum"]/div/img/@src'
PRODUCT_SPECS_XPATH = '//div[@class="isq-container  "]//table'
ALTERNATE_PRODUCT_SPECS_XPATH = '//div[@class="  pro-descN"]/div/table'
PRODUCT_DESCRIPTION_XPATH = '//div[@class="  pro-descN"]'
PRODUCT_DESCRIPTION_TEXT_XPATH = '//div[@class="  pro-descN"]/text()'
PRODUCT_ADDITIONAL_INFO_XPATH = '//div[@class="pdest1 color"]//table'
COMPANY_DETAILS_XPATH = '//div[@class="lh21 pdinb wid3 mb20 verT"]'
COMPANY_DESCRIPTION_XPATH = './/div[@id="aboutUs"]'
COMPANY_DESCRIPTION_TEXT_XPATH = './/div[@id="aboutUs"]/div/div[3]//text()'
COMPANY_ADDRESS_XPATH = './/span[@class="color1 dcell verT fs13"]'
COMPANY_ADDRESS_TEXT_XPATH = './/span[@class="color1 dcell verT fs13"]/text()'
SELLER_NAME_XPATH = './/div[@id="supp_nm"]'
SELLER_NAME_TEXT_XPATH = './/div[@id="supp_nm"]/text()'
COMPANY_URL_XPATH = './/a[@class="color1 utd"]'
COMPANY_URL_HREF_XPATH = './/a[@class="color1 utd"]/@href'
GMAPS_XPATH = './/a[@class="color3 pd_txu gtdir on"]'
GMAPS_HREF_XPATH = './/a[@class="color3 pd_txu gtdir on"]/@href'
PRODUCT_CATEGORY = '//div[@id="brdcrmb"]//text()'

# MESSAGE
UNABLE_TO_FETCH_DATA_MESSAGE = "Failed to fetch %s"

# Constants for justdial scraper

DOC_PATTERN = r"\/([\w-]*_BZDET)[\/|\?]"
CITY_PATTERN = r"\/Mumbai\/"
PINCODE_PATTERN = r"\b\d{6}\b"

CUSTOM_SETTINGS = {
    "LOG_LEVEL": "WARNING",
    "DEFAULT_REQUEST_HEADERS": {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/x-www-form-urlencoded",
        "email": "",
        "mobile": "",
        "name": "",
        "origin": "https://www.justdial.com",
        "priority": "u=1, i",
        "sec-ch-ua": '"Google Chrome";v="129", "Not=A?Brand";v="8", "Chromium";v="129"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Linux"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "sid": "",
        "user-agent": USER_AGENT,
    },
}

JUSTDIAL_BASE_URL = "https://www.justdial.com"
WRAPI_URL_PATTERN = ".*api/wrapi?.*apifile=searchziva.*"

PARENT_DIV_XPATH = "resultbox_info"
URL_DIV_XPATH = "resultbox_title_anchorbox"
MAY_BE_LATER_CLASS_NAME = "maybelater"

GST_BASE_URL = "http://sheet.gstincheck.co.in/check"
GST_RETURNS_BASE_URL = "http://sheet.gstincheck.co.in/check-return"

LOCAL_BUSINESS_DATA_URL = "https://local-business-data.p.rapidapi.com/search"

# RANKING FIELDS WITH WEIGHTS
GST_FIELD_WEIGHTS = {
    "gstDetails.adhrVFlag": 1,  # if yes, then +1
    "gstDetails.ekycVFlag": 1,  # if yes, then +1
    "gstDetails.sts": 1,  # if active, then +3
    "gstDetails.isFieldVisitConducted": 1,  # if yes, then +1
}
# TOTAL: 10

SCRAPED_DATA_FIELD_WEIGHTS = {
    "company": 1,
    "companyDescription": 1,
    "address": 1,
    "locality": 1,
    "city": 1,
    "email": 1,
    "phone": 3,
    "website": 1,
    "turnover": 3,
    "gst": 5,
    "owner": 1,
    "gmaps": 2,
}
# TOTAL: 21

GBD_FIELD_WEIGHTS = {
    "matchedVendor.business_status": 1, # if OPEN, +1
    "matchedVendor.verified": 1,        # # if True, +1
    "matchedVendor.opening_status": 1,
    "matchedVendor.website": 1,
    "matchedVendor.emails_and_contacts.phone_numbers": 1,
    "matchedVendor.emails_and_contacts.emails": 1,
    "matchedVendor.emails_and_contacts.facebook":1,
    "matchedVendor.emails_and_contacts.instagram":1,
    "matchedVendor.emails_and_contacts.youtube":1,
    "matchedVendor.working_hours":1,
    "matchedVendor.place_link":1
}
# TOTAL: 10

# Thresholds to match google business data with raw sellers
NAME_MATCH_THRESHOLD = 85
ADDRESS_MATCH_THRESHOLD = 60