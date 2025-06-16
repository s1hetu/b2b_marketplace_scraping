import argparse
import multiprocessing
from apps.deldure_scraper import app as deldure_app
from apps.indiamart_scraper import app as indiamart_app
import libs.utils.config as config
from libs.utils.log_services.logger import setup_logger
from waitress import serve

logger = setup_logger("app")

app_name = {
    "deldure": ["🕷 🕸", config.DELDURE_PORT, deldure_app],
    "indiamart": ["🕷 🕸", config.INDIAMART_PORT, indiamart_app],
}


def start_server(app, port):
    serve(app, port=port)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Start Flask apps")
    parser.add_argument("--all", action="store_true", help="Start all the apps")

    for app_key in app_name.keys():
        parser.add_argument(f"--{app_key}", action="store_true", help=f"Start the {app_key} app")

    args = parser.parse_args()
    logger.info("Server is running!!!🚀")
    processes = []
    if args.all:
        for app_key, app_details in app_name.items():
            processes.append(
                multiprocessing.Process(
                    target=start_server, args=(app_details[2], app_details[1]), name=app_key
                )
            )
    else:
        # Start only the selected apps
        for arg, is_provided in args._get_kwargs():
            if is_provided and arg in app_name:
                app_details = app_name[arg]
                processes.append(
                    multiprocessing.Process(
                        target=start_server, args=(app_details[2], app_details[1]), name=arg
                    )
                )

    # Start the selected processes
    for process in processes:
        process.start()
        logger.info(
            f"Started {process.name} process {app_name[process.name][0]} on port {app_name[process.name][1]}"
        )
    # Wait for all processes to finish
    for process in processes:
        process.join()
        logger.info(f"{process.name} process has finished ⛽🚀")
