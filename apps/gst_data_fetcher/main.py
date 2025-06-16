"""
Main entry point to start the fetching GST data
To run:  python3 -m apps.gst_data_fetcher.main
"""
from apps.gst_data_fetcher.helpers.fetch_gst_data import main

if __name__ == "__main__":
    gst_details = main()