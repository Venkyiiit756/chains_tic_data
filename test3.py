import cloudscraper
import logging
import os
from datetime import datetime
import pytz
import json
import urllib.parse as urlparse
import time
import random
from concurrent.futures import ThreadPoolExecutor, as_completed

# Configure logging to file and console with DEBUG level for detailed logs
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("fetch_data.log"),
        logging.StreamHandler()  # Console output
    ]
)
logger = logging.getLogger(__name__)

# Load city data from JSON file
def load_cities(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            cities = json.load(f)
            logger.debug(f"Loaded {len(cities)} cities from {file_path}.")
            print(f"Loaded {len(cities)} cities from '{file_path}'.")
            return cities
    except Exception as e:
        logger.error(f"Error loading cities from {file_path}: {e}")
        print(f"Error loading cities from '{file_path}': {e}")
        return []

# Example: Load cities from 'region_data_output.json'
# Ensure 'region_data_output.json' exists with appropriate data
cities = load_cities('region_data_output.json')

def fetch_data_for_city(city, retries=3, backoff_factor=2):
    url = (
        f"https://in.bookmyshow.com/api/movies-data/showtimes-by-event?"
        f"appCode=MOBAND2&appVersion=14304&language=en&eventCode=ET00310216&"
        f"regionCode={city['region_code']}&subRegion={city['sub_region_code']}&"
        f"bmsId=1.21345445.1703250084656&token=67x1xa33b4x422b361ba&"
        f"lat={city['latitude']}&lon={city['longitude']}&query="
    )
    
    headers = {
        "Host": "in.bookmyshow.com",
        "x-bms-id": "1.21345445.1703250084656",
        "x-region-code": city['region_code'],
        "x-subregion-code": city['sub_region_code'],
        "x-region-slug": city['region_slug'],
        "x-platform": "AND",
        "x-platform-code": "ANDROID",
        "x-app-code": "MOBAND2",
        "x-device-make": "Google-Pixel XL",
        "x-screen-height": "2392",
        "x-screen-width": "1440",
        "x-screen-density": "3.5",
        "x-app-version": "14.3.4",
        "x-app-version-code": "14304",
        "x-network": "Android | WIFI",
        "x-latitude": city['latitude'],
        "x-longitude": city['longitude'],
        "x-ab-testing": (
            "adtechHPSlug=default&adtechHPCarousel=variant&adQtySelection=default&"
            "cinemaListingRevamp=variant&cinemaChipFilters=default&comingSoonPznV1=default&"
            "dealsReward=default&dealsRewardV2=default&dealHeaderTypeExp2=default&"
            "discoveryOnlineEvents=variant&ehpChristmas=default&ehpCollectionV1=default&"
            "ehpCollectionV2=default&ehpMarqueePosV3=null&ehpSneakPeekPzn=default&"
            "eventCollection=null&fnbPTDE=null&fnbPTDEV2=default&leDropOffV2=default&"
            "leMultiDayPassV2=default&leSoldOutSimilar=variant&leCoupons=default&"
            "leHLPExp1=default&leHLPExp2=default&leHLPExp3=default&leHLPExp4=default&"
            "locationIntelligenceFeature=default&locIntelligenceV3=&locIntelligenceV4=variant&"
            "mlpTrailerIngress=default&mlpTrailerIngressV2=default&moviesBestSeatsV2=default&"
            "moviesBestSeatsV3=default&moviesCoachmarkV3=variant&moviesHPV4=default&"
            "moviesHPV5=default&mspInnovativeAdV2=default&offersFilmyPassV2=null&"
            "offersRevampExp1=default&ospQuickpay=variant&peppoPaymentType=null&"
            "playLPRevamp=default&pricingExp7=default&ptcxModifyBook=default&ptdeCollateral=default&"
            "ptdeDeals=default&ptmDealsFnBWidget=null&ptmDiwaliCollateral=default&"
            "ptmRewardsWidgetTypeV2=variant&ptmXmasCollateral=default&pznHnyWidgetV1=default&"
            "showtimeRevampV1=default&showtimeRevExp12=default&showTimeViewLocation=default&"
            "showTimeViewRegion=default&skipCVV=Default&socialNudgeExp8=default&"
            "surfaceReviewsMSPV2=variant&surfaceOfferMSPSL=variant&tncLocation=variant"
        ),
        "x-advertiser-id": "a9b0e8d0-b8f3-49f0-a662-7e96354def78",
        "x-geohash": "tdr",
        "x-li-flow": "false",
        "x-location-selection": "manual",
        "x-location-shared": "false",
        "lang": "en",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel XL Build/SP2A.220505.008)"
    }

    # Initialize a cloudscraper instance
    scraper = cloudscraper.create_scraper()

    for attempt in range(retries):
        try:
            logger.debug(f"Attempt {attempt + 1}: Sending GET request to {url}")
            print(f"Fetching data for {city['city_code']} (Attempt {attempt + 1})...")
            response = scraper.get(url, headers=headers, timeout=30)

            # Raise an exception for HTTP error codes
            response.raise_for_status()

            # Parse JSON response
            data = response.json()
            logger.info(f"Data fetched successfully for city: {city['city_code']}")
            print(f"Successfully fetched data for {city['city_code']}.")
            return data

        except cloudscraper.exceptions.CloudflareChallengeError as e:
            logger.error(f"Cloudflare challenge error for city {city['city_code']}: {e}")
            print(f"Cloudflare challenge error for {city['city_code']}: {e}")
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for city {city['city_code']}: {e}")
            print(f"HTTP error for {city['city_code']}: {e}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception for city {city['city_code']}: {e}")
            print(f"Request exception for {city['city_code']}: {e}")
        except ValueError:
            # If response is not JSON, log raw text
            logger.warning(f"Response is not in JSON format for city {city['city_code']}.")
            print(f"Non-JSON response for {city['city_code']}. Saving raw text.")
            return response.text

        # Exponential backoff before retrying
        sleep_time = backoff_factor ** attempt
        logger.debug(f"Sleeping for {sleep_time} seconds before retrying.")
        print(f"Retrying in {sleep_time} seconds...")
        time.sleep(sleep_time)

    logger.error(f"All {retries} attempts failed for city {city['city_code']}.")
    print(f"Failed to fetch data for {city['city_code']} after {retries} attempts.")
    return None

def save_data(directory_name, city_code, data):
    try:
        if isinstance(data, dict):
            # Define filename
            filename = f"{city_code}.json"
            # Full path to save the JSON file
            file_path = os.path.join(directory_name, filename)
            # Save JSON data to file
            with open(file_path, 'w', encoding='utf-8') as json_file:
                json.dump(data, json_file, ensure_ascii=False, indent=4)
                logger.info(f"Data saved to {file_path}")
                print(f"Saved JSON data for {city_code} to {file_path}.")
        else:
            # If data is raw text
            filename = f"{city_code}.txt"
            file_path = os.path.join(directory_name, filename)
            with open(file_path, 'w', encoding='utf-8') as text_file:
                text_file.write(data)
                logger.info(f"Raw response saved to {file_path}")
                print(f"Saved raw response for {city_code} to {file_path}.")
    except Exception as e:
        logger.error(f"Error saving data for city {city_code}: {e}")
        print(f"Error saving data for {city_code}: {e}")

def fetch_and_save_all_cities_parallel():
    # Get current IST time
    ist_timezone = pytz.timezone('Asia/Kolkata')
    current_ist_time = datetime.now(ist_timezone)
    formatted_time = current_ist_time.strftime('%Y%m%d_%H%M%S')  # Example: 20240924_153045

    # Define base directory
    base_directory = 'data'

    # Define directory name using current IST time
    directory_name = os.path.join(base_directory, formatted_time)

    # Create base directory if it doesn't exist
    if not os.path.exists(base_directory):
        os.makedirs(base_directory)
        logger.info(f"Created base directory: {base_directory}")
        print(f"Created base directory: '{base_directory}'.")

    # Create time-stamped directory
    if not os.path.exists(directory_name):
        os.makedirs(directory_name)
        logger.info(f"Created directory: {directory_name}")
        print(f"Created time-stamped directory: '{directory_name}'.")

    # Define the number of worker threads
    max_workers = min(10, len(cities))  # Adjust based on your needs
    logger.debug(f"Using {max_workers} worker threads for fetching data.")
    print(f"Starting data fetch with {max_workers} worker threads.")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all fetch tasks
        future_to_city = {executor.submit(fetch_data_for_city, city): city for city in cities}
        total_cities = len(cities)
        logger.debug(f"Submitted {total_cities} fetch tasks.")
        print(f"Submitted {total_cities} fetch tasks.")

        completed = 0
        success_count = 0
        failure_count = 0

        for future in as_completed(future_to_city):
            city = future_to_city[future]
            try:
                data = future.result()
                if data:
                    save_data(directory_name, city['city_code'], data)
                    success_count += 1
                else:
                    logger.warning(f"No data returned for city {city['city_code']}.")
                    print(f"No data returned for {city['city_code']}.")
                    failure_count += 1

                completed += 1
                print(f"Progress: {completed}/{total_cities} cities processed.")

                # Optional: Random delay to be polite
                delay = random.uniform(1, 3)
                logger.debug(f"Sleeping for {delay:.2f} seconds before next request.")
                print(f"Sleeping for {delay:.2f} seconds before next request.")
                time.sleep(delay)
            except Exception as e:
                logger.error(f"Unhandled exception for city {city['city_code']}: {e}")
                print(f"Unhandled exception for {city['city_code']}: {e}")
                failure_count += 1

    # Summary
    summary = f"Data fetching completed: {success_count} succeeded, {failure_count} failed."
    print(summary)
    logger.info(summary)

if __name__ == "__main__":
    fetch_and_save_all_cities_parallel()
