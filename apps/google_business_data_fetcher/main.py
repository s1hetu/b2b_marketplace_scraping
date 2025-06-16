"""
Main entry point to start the fetching Google business data
To run:  python3 -m apps.google_business_data_fetcher.main
"""
from apps.google_business_data_fetcher.helpers.fetch_google_business_data import get_google_business_data

if __name__ == "__main__":
    business_data = get_google_business_data()