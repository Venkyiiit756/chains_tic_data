import requests
import pandas as pd
import time
from datetime import datetime
import pytz

def fetch_showtimes(city_code, city_name):
    """
    Fetches showtimes for a given city and saves the data to an Excel file.

    Parameters:
    - city_code (str): The region/sub-region code for the city (e.g., 'HYD', 'BANG', 'CHEN').
    - city_name (str): The name of the city (e.g., 'HYD', 'Bangalore', 'Chennai').
    """
    # Define the base URL with placeholders for region and sub-region codes
    base_url = "https://in.bookmyshow.com/api/movies-data/showtimes-by-event"
    
    # Common query parameters
    params = {
        "appCode": "MOBAND2",
        "appVersion": "14304",
        "language": "en",
        "eventCode": "ET00310216",
        "regionCode": city_code,
        "subRegion": city_code,
        "bmsId": "1.21345445.1703250084656",
        "token": "67x1xa33b4x422b361ba",
        "lat": "12.971599",  # These could be dynamic based on city if needed
        "lon": "77.59457",
        "query": ""
    }
    
    # Construct the full URL with query parameters
    response_url = f"{base_url}?{'&'.join([f'{key}={value}' for key, value in params.items()])}"
    
    # Define headers with dynamic region and sub-region codes
    headers = {
        "Host": "in.bookmyshow.com",
        "x-bms-id": "1.21345445.1703250084656",
        "x-region-code": city_code,
        "x-subregion-code": city_code,
        "x-region-slug": city_name.lower(),  # Assuming slug is lowercase city name
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
        "x-latitude": "12.971599",  # These could be dynamic based on city if needed
        "x-longitude": "77.59457",
        "x-ab-testing": "adtechHPSlug=default&adtechHPCarousel=variant&adQtySelection=default&cinemaListingRevamp=variant&cinemaChipFilters=default&comingSoonPznV1=default&dealsReward=default&dealsRewardV2=default&dealHeaderTypeExp2=default&discoveryOnlineEvents=variant&ehpChristmas=default&ehpCollectionV1=default&ehpCollectionV2=default&ehpMarqueePosV3=null&ehpSneakPeekPzn=default&eventCollection=null&fnbPTDE=null&fnbPTDEV2=default&leDropOffV2=default&leMultiDayPassV2=default&leSoldOutSimilar=variant&leCoupons=default&leHLPExp1=default&leHLPExp2=default&leHLPExp3=default&leHLPExp4=default&locationIntelligenceFeature=default&locIntelligenceV3=&locIntelligenceV4=variant&mlpTrailerIngress=default&mlpTrailerIngressV2=default&moviesBestSeatsV2=default&moviesBestSeatsV3=default&moviesCoachmarkV3=variant&moviesHPV4=default&moviesHPV5=default&mspInnovativeAdV2=default&offersFilmyPassV2=null&offersRevampExp1=default&ospQuickpay=variant&peppoPaymentType=null&playLPRevamp=default&pricingExp7=default&ptcxModifyBook=default&ptdeCollateral=default&ptdeDeals=default&ptmDealsFnBWidget=null&ptmDiwaliCollateral=default&ptmRewardsWidgetTypeV2=variant&ptmXmasCollateral=default&pznHnyWidgetV1=default&showtimeRevampV1=default&showtimeRevExp12=default&showTimeViewLocation=default&showTimeViewRegion=default&skipCVV=Default&socialNudgeExp8=default&surfaceReviewsMSPV2=variant&surfaceOfferMSPSL=variant&tncLocation=variant",
        "x-advertiser-id": "a9b0e8d0-b8f3-49f0-a662-7e96354def78",
        "x-geohash": "tdr",
        "x-li-flow": "false",
        "x-location-selection": "manual",
        "x-location-shared": "false",
        "lang": "en",
        "user-agent": "Dalvik/2.1.0 (Linux; U; Android 12; Pixel XL Build/SP2A.220505.008)"
    }
    
    try:
        # Make the GET request with headers and parameters
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()  # Check for HTTP errors

        # Parse the JSON response
        data = response.json()

        # Initialize an empty list to store results
        results = []

        # Traverse the JSON data to extract required information
        for show_detail in data.get('ShowDetails', []):
            for venue in show_detail.get('Venues', []):
                venue_name = venue.get('VenueName', '')
                for show_time in venue.get('ShowTimes', []):
                    show_time_str = show_time.get('ShowTime', '')
                    for category in show_time.get('Categories', []):
                        max_seats = int(category.get('MaxSeats', '0'))
                        seats_avail = int(category.get('SeatsAvail', '0'))
                        booked_tickets = max_seats - seats_avail
                        current_price = float(category.get('CurPrice', '0'))

                        # Calculate BookedGross and TotalGross
                        booked_gross = booked_tickets * current_price
                        total_gross = max_seats * current_price

                        # Append the extracted data to results list
                        results.append({
                            'VenueName': venue_name,
                            'ShowTime': show_time_str,
                            'Category': category.get('PriceDesc', ''),
                            'MaxSeats': max_seats,
                            'SeatsAvailable': seats_avail,
                            'BookedTickets': booked_tickets,
                            'CurrentPrice': current_price,
                            'BookedGross': booked_gross,
                            'TotalGross': total_gross
                        })

        # Create a DataFrame from the results
        df = pd.DataFrame(results)
        print(f"Data for {city_name}:")
        print(df.head())  # Display first few rows for verification

        # Generate timestamp in Indian Standard Time (IST)
        ist = pytz.timezone('Asia/Kolkata')
        timestamp = datetime.now(ist).strftime('%Y%m%d_%H%M%S')

        # Define the Excel filename
        filename = f"{city_name}_{timestamp}.xlsx"

        # Save the DataFrame to an Excel file with two sheets
        with pd.ExcelWriter(filename) as writer:
            # Sheet1 with detailed data
            df.to_excel(writer, sheet_name='DetailedData', index=False)

            # Sheet2 with aggregated data
            # Remove 'Category' and 'CurrentPrice' before grouping
            grouped_df = df.drop(columns=['Category', 'CurrentPrice']).groupby(['VenueName', 'ShowTime'], as_index=False).sum()

            grouped_df.to_excel(writer, sheet_name='AggregatedData', index=False)

        print(f"Data for {city_name} has been saved to '{filename}' with two sheets.\n")

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred for {city_name}: {http_err}\n')
    except requests.exceptions.RequestException as err:
        print(f'Request error occurred for {city_name}: {err}\n')
    except Exception as e:
        print(f'An error occurred for {city_name}: {e}\n')

def main():
    # List of cities with their corresponding codes and names
    city_info = [
        {'code': 'BANG', 'name': 'Bangalore'},
    ]

    for city in city_info:
        fetch_showtimes(city['code'], city['name'])
        time.sleep(20)  # Wait for 2 seconds between requests to prevent rate limiting

if __name__ == "__main__":
    main()
