from flask import request, make_response
from apps.deldure_scraper import app
from libs.utils.log_services.logger import setup_logger
import libs.utils.config as config

logger = setup_logger("deldure_router")

"""
Scrapes all the necessary data from the deldure website
"""

@app.route("/", methods=["GET"])
def index():
    response = make_response(
            "Deldure Scraper",
            200
        )
    return response

@app.route("/deldure-scraper", methods=["GET"])
def deldure_scraper():
    try:
        response = "Hello, World!"
        pass
        return response
    except Exception as e:
        return e