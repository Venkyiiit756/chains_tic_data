import cloudscraper

def fetch_cinepolis_api():
    # Create a cloudscraper instance
    scraper = cloudscraper.create_scraper()

    headers = {
        "accept": "application/json",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "authority": "api_new.cinepolisindia.com",
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

    # API URL
    api_url = "
    "

    # Send a GET request to the API without verify=False
    response = scraper.get(api_url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Print the JSON response
        api_data = response.json()
        print(api_data)
    else:
        print(f"Failed to fetch data: {response.status_code}")

# Run the function
fetch_cinepolis_api()
