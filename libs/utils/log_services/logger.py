import logging
from logging.handlers import RotatingFileHandler
import os
from os.path import basename
import zipfile
from colorlog import ColoredFormatter
from libs.utils import config as config

def create_folder_if_not_exists(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def setup_logger(app_name):
    logger = logging.getLogger(app_name)
    logger.propagate = False  # Prevent propagation to the root logger

    logger.setLevel(logging.INFO)
    logger_path = os.path.join("logs")
    create_folder_if_not_exists(logger_path)
    log_file_path = os.path.join("logs", f"{app_name}.log")

    def rotator(source, dest):
        zipfile.ZipFile(dest, "w", zipfile.ZIP_DEFLATED).write(source, basename(source))
        os.remove(source)

    fileHandler = RotatingFileHandler(log_file_path, backupCount=10, maxBytes=10240)
    fileHandler.namer = lambda name: name.replace(".log", "") + ".zip"
    fileHandler.rotator = rotator

    logFormatter = logging.Formatter(
        "%(asctime)s - %(levelname)s -%(name)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    fileHandler.setFormatter(logFormatter)

    logger.addHandler(fileHandler)

    # Create a colored log formatter for the console
    consoleFormatter = ColoredFormatter(
        "%(log_color)s%(asctime)s - %(levelname)s -%(name)s - %(filename)s - %(funcName)s - %(lineno)s - %(message)s %(reset)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            "DEBUG": "cyan",
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "CRITICAL": "red,bg_white",
        },
    )

    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(consoleFormatter)
    logger.addHandler(consoleHandler)

    return logger