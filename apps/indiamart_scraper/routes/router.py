from flask import request, make_response
from apps.indiamart_scraper import app
from libs.utils.log_services.logger import setup_logger
import libs.utils.config as config

logger = setup_logger("indiamart_scrapper")

"""
Scrapes all the necessary data from the indiamart website
"""

@app.route("/", methods=["GET"])
def index():
    response = make_response(
            "IndiaMart Scraper",
            200
        )
    return response
