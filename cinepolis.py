import requests

def url_config():
    movie_id = "HO00015515"
    date = "2024-09-07"
    city_id = "35"
    experience = ""
    isVip = "N"
    config_api_url = f"https://api_new.cinepolisindia.com/api/movies/show-times/{movie_id}/?request_type=get-show-times&show_date={date}&movie_id={movie_id}&city_id={city_id}&experience={experience}&isVip={isVip}/"
    return config_api_url

def get_cinepolis_session_data():
    api_url = url_config()
    print(api_url)

    # Headers that mimic the browser request
    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "origin": "https://cinepolisindia.com",
        "referer": "https://cinepolisindia.com/",
        "sec-ch-ua": '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36"
    }

     # Send the request with headers and cookies
    response = requests.get(api_url, headers=headers, verify=False)

    if response.status_code == 200:
        print(response.json())  # Output the response data
    else:
        print(f"Error in fetching the data: error code: {response.status_code}")

get_cinepolis_session_data()

