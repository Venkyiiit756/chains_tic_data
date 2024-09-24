import cloudscraper
import logging
import os
from datetime import datetime
import pytz
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def fetch_data():
    url = (
        "https://in.bookmyshow.com/api/movies-data/showtimes-by-event?"
        "appCode=MOBAND2&appVersion=14304&language=en&eventCode=ET00310216&"
        "regionCode=HYD&subRegion=HYD&bmsId=1.21345445.1703250084656&"
        "token=67x1xa33b4x422b361ba&lat=12.971599&lon=77.59457&query="
    )
    
    headers = {
        "Host": "in.bookmyshow.com",
        "x-bms-id": "1.21345445.1703250084656",
        "x-region-code": "HYD",
        "x-subregion-code": "HYD",
        "x-region-slug": "hyderabad",
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
        "x-latitude": "12.971599",
        "x-longitude": "77.59457",
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

    try:
        logger.info(f"Sending GET request to {url}")
        response = scraper.get(url, headers=headers, timeout=30)

        # Raise an exception for HTTP error codes
        response.raise_for_status()

        # Parse JSON response
        data = response.json()
        logger.info("Data fetched successfully.")

        # Get current IST time
        ist_timezone = pytz.timezone('Asia/Kolkata')
        current_ist_time = datetime.now(ist_timezone)
        formatted_time = current_ist_time.strftime('%Y%m%d_%H%M%S')  # Example: 20240924_153045

        # Define directory name using current IST time
        directory_name = formatted_time

        # Create directory if it doesn't exist
        if not os.path.exists(directory_name):
            os.makedirs(directory_name)
            logger.info(f"Created directory: {directory_name}")

        # Extract city code from headers or URL
        # Assuming 'x-region-code' header contains the city code
        city_code = headers.get('x-region-code', 'UNKNOWN')
        if not city_code:
            # Fallback: Extract from URL parameters
            import urllib.parse as urlparse
            parsed_url = urlparse.urlparse(url)
            query_params = urlparse.parse_qs(parsed_url.query)
            city_code = query_params.get('regionCode', ['UNKNOWN'])[0]

        # Define filename
        filename = f"{city_code}.json"

        # Full path to save the JSON file
        file_path = os.path.join(directory_name, filename)

        # Save JSON data to file
        with open(file_path, 'w', encoding='utf-8') as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
            logger.info(f"Data saved to {file_path}")

    except cloudscraper.exceptions.CloudflareChallengeError as e:
        logger.error(f"Cloudflare challenge error: {e}")
    except requests.exceptions.HTTPError as e:
        logger.error(f"HTTP error occurred: {e}")
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception: {e}")
    except ValueError:
        # If response is not JSON, print raw text
        logger.warning("Response is not in JSON format.")
        raw_file_path = os.path.join(directory_name, f"{city_code}.txt")
        with open(raw_file_path, 'w', encoding='utf-8') as text_file:
            text_file.write(response.text)
            logger.info(f"Raw response saved to {raw_file_path}")

if __name__ == "__main__":
    fetch_data()
