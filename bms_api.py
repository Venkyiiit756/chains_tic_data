import requests
import pandas as pd

def fetch_showtimes():
    url = "https://in.bookmyshow.com/api/movies-data/showtimes-by-event?appCode=MOBAND2&appVersion=14304&language=en&eventCode=ET00310216&regionCode=CHEN&subRegion=CHEN&bmsId=1.21345445.1703250084656&token=67x1xa33b4x422b361ba&lat=12.971599&lon=77.59457&query="

    headers = {
        "Host": "in.bookmyshow.com",
        "x-bms-id": "1.21345445.1703250084656",
        "x-region-code": "CHEN",
        "x-subregion-code": "CHEN",
        "x-region-slug": "chennai",
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
        # Make the GET request with headers
        response = requests.get(url, headers=headers)
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
        print(df)

        # Save the DataFrame to an Excel file with two sheets
        with pd.ExcelWriter('showtimes.xlsx') as writer:
            # Sheet1 with detailed data
            df.to_excel(writer, sheet_name='Sheet1', index=False)

            # Sheet2 with aggregated data
            # Remove 'Category' and 'CurrentPrice' before grouping
            grouped_df = df.drop(columns=['Category', 'CurrentPrice']).groupby(['VenueName', 'ShowTime'], as_index=False).sum()

            grouped_df.to_excel(writer, sheet_name='Sheet2', index=False)

        print("Data has been saved to 'showtimes.xlsx' with two sheets.")

        return df

    except requests.exceptions.HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except requests.exceptions.RequestException as err:
        print(f'Error occurred: {err}')
    except Exception as e:
        print(f'An error occurred: {e}')

# Call the function
fetch_showtimes()
