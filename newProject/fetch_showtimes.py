import requests
import pandas as pd
from datetime import datetime
import pytz

def fetch_showtimes(city_code, city_name):
    print(f"Fetching showtimes for {city_name}...")
    base_url = "https://in.bookmyshow.com/api/movies-data/showtimes-by-event"
    params = {
        "appCode": "MOBAND2",
        "appVersion": "14304",
        "language": "en",
        "eventCode": "ET00310216",
        "regionCode": city_code,
        "subRegion": city_code,
        "bmsId": "1.21345445.1703250084656",
        "token": "67x1xa33b4x422b361ba",
        "lat": "12.971599",
        "lon": "77.59457",
        "query": ""
    }
    headers = {
        "Host": "in.bookmyshow.com",
        "x-bms-id": "1.21345445.1703250084656",
        "x-region-code": city_code,
        "x-subregion-code": city_code,
        "x-region-slug": city_name.lower(),
        "x-platform": "AND",
        "x-platform-code": "ANDROID",
        "x-app-code": "MOBAND2",
        "user-agent": "Dalvik/2.1.0 (Linux; U; Android 13; Pixel XL Build/SP2A.220505.008)"
    }
    
    try:
        print(f"Sending request to URL: {base_url} with params: {params} and headers: {headers}")
        response = requests.get(base_url, headers=headers, params=params)
        response.raise_for_status()
        print(f"Response status code: {response.status_code}")
        data = response.json()
        print(f"Response data: {data}")

        results = []
        for show_detail in data.get('ShowDetails', []):
            print(f"Processing show detail: {show_detail}")
            for venue in show_detail.get('Venues', []):
                venue_name = venue.get('VenueName', '')
                print(f"Processing venue: {venue_name}")
                for show_time in venue.get('ShowTimes', []):
                    show_time_str = show_time.get('ShowTime', '')
                    print(f"Processing show time: {show_time_str}")
                    for category in show_time.get('Categories', []):
                        max_seats = int(category.get('MaxSeats', '0'))
                        seats_avail = int(category.get('SeatsAvail', '0'))
                        booked_tickets = max_seats - seats_avail
                        current_price = float(category.get('CurPrice', '0'))

                        booked_gross = booked_tickets * current_price
                        total_gross = max_seats * current_price

                        print(f"Processed category: {category.get('PriceDesc', '')}, MaxSeats: {max_seats}, SeatsAvailable: {seats_avail}, BookedTickets: {booked_tickets}, CurrentPrice: {current_price}")

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

        df = pd.DataFrame(results)
        print(f"Data fetched for {city_name}. DataFrame shape: {df.shape}")
        return df
    except requests.exceptions.RequestException as e:
        print(f"Request error occurred for {city_name}: {e}")
        return pd.DataFrame()
