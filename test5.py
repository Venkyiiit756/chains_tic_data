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
import requests  # Ensure requests is imported
from bs4 import BeautifulSoup  # For parsing HTML if needed
import threading

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

# List of User-Agents for rotation
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/115.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) "
    "Version/14.0.3 Safari/605.1.15",
    # Add more User-Agents as needed
]

def fetch_proxies_from_multiple_sources():
    """
    Fetches proxies from multiple free proxy providers.
    Returns:
        list: Combined list of proxies in 'ip:port' format.
    """
    proxies = []
    
    # Source 1: ProxyScrape
    proxy_api_url = (
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=10000&"
        "country=all&ssl=yes&anonymity=all"
    )
    try:
        response = requests.get(proxy_api_url, timeout=30)
        response.raise_for_status()
        fetched_proxies = response.text.split('\n')
        fetched_proxies = [proxy.strip() for proxy in fetched_proxies if proxy.strip()]
        proxies.extend(fetched_proxies)
        logger.debug(f"Fetched {len(fetched_proxies)} proxies from ProxyScrape.")
        print(f"Fetched {len(fetched_proxies)} proxies from ProxyScrape.")
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching proxies from ProxyScrape: {e}")
        print(f"Error fetching proxies from ProxyScrape: {e}")
    
    # Source 2: Free Proxy List
    free_proxy_url = "https://free-proxy-list.net/"
    try:
        response = requests.get(free_proxy_url, timeout=30)
        response.raise_for_status()
        # Parse HTML to extract proxies
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', attrs={'id': 'proxylisttable'})
        for row in table.tbody.find_all('tr'):
            cols = row.find_all('td')
            ip = cols[0].text.strip()
            port = cols[1].text.strip()
            https = cols[6].text.strip()
            if https == 'yes':
                proxy = f"{ip}:{port}"
                proxies.append(proxy)
        logger.debug(f"Fetched proxies from Free Proxy List: {len(proxies)} total proxies.")
        print(f"Fetched proxies from Free Proxy List: {len(proxies)} total proxies.")
    except Exception as e:
        logger.error(f"Error fetching proxies from Free Proxy List: {e}")
        print(f"Error fetching proxies from Free Proxy List: {e}")
    
    # Add more sources similarly...
    
    return proxies

def validate_proxy(proxy, test_url="https://httpbin.org/get", timeout=10):
    """
    Validates a single proxy by attempting to connect to a test URL.
    Args:
        proxy (str): Proxy in 'ip:port' format.
        test_url (str): URL to test the proxy against.
        timeout (int): Timeout in seconds for the test request.
    Returns:
        bool: True if proxy is valid, False otherwise.
    """
    proxies = {
        "http": f"http://{proxy}",
        "https": f"http://{proxy}",  # Using HTTP proxy for HTTPS requests
    }
    try:
        response = requests.get(test_url, proxies=proxies, timeout=timeout)
        if response.status_code == 200:
            logger.debug(f"Proxy {proxy} is valid.")
            return True
    except requests.exceptions.RequestException:
        pass
    logger.debug(f"Proxy {proxy} is invalid.")
    return False

def get_valid_proxies(proxy_list, max_workers=50):
    """
    Filters the provided proxy list and returns only the valid proxies.
    Args:
        proxy_list (list): List of proxies in 'ip:port' format.
        max_workers (int): Number of threads for concurrent validation.
    Returns:
        list: List of valid proxies.
    """
    valid_proxies = []
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_proxy = {executor.submit(validate_proxy, proxy): proxy for proxy in proxy_list}
        for future in as_completed(future_to_proxy):
            proxy = future_to_proxy[future]
            try:
                if future.result():
                    valid_proxies.append(proxy)
            except Exception as e:
                logger.error(f"Error validating proxy {proxy}: {e}")
    logger.info(f"Validated proxies: {len(valid_proxies)} out of {len(proxy_list)}")
    print(f"Validated proxies: {len(valid_proxies)} out of {len(proxy_list)}")
    return valid_proxies

def load_cities(file_path):
    """
    Loads city data from a JSON file.
    Args:
        file_path (str): Path to the JSON file containing city data.
    Returns:
        list: List of city dictionaries.
    """
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

def fetch_data_for_city(city, proxies, retries=3, backoff_factor=2):
    """
    Fetches data for a single city using a proxy from the provided proxy list.
    Args:
        city (dict): City data dictionary.
        proxies (list): List of validated proxies.
        retries (int): Number of retry attempts.
        backoff_factor (int): Backoff factor for sleep between retries.
    Returns:
        dict or str: JSON data if successful, raw text otherwise.
    """
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
        "lang": "en",
        "User-Agent": random.choice(user_agents)  # Rotate User-Agent
    }

    scraper = cloudscraper.create_scraper()

    for attempt in range(retries):
        if not proxies:
            logger.error("Proxy pool is empty. Exiting.")
            print("Proxy pool is empty. Exiting.")
            return None
        proxy = random.choice(proxies)
        proxies_dict = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}",  # Using HTTP proxy for HTTPS requests
        }
        try:
            logger.debug(f"Attempt {attempt + 1}: Sending GET request to {url} using proxy {proxy}")
            print(f"Fetching data for {city['city_code']} (Attempt {attempt + 1}) using proxy {proxy}...")
            
            response = scraper.get(url, headers=headers, proxies=proxies_dict, timeout=30)

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
            proxies.remove(proxy)  # Remove faulty proxy
        except requests.exceptions.HTTPError as e:
            logger.error(f"HTTP error for city {city['city_code']}: {e}")
            print(f"HTTP error for {city['city_code']}: {e}")
            # Log response content if available
            if response.content:
                try:
                    content = response.json()
                    logger.debug(f"Response content for {city['city_code']}: {content}")
                    print(f"Response content for {city['city_code']}: {content}")
                except ValueError:
                    # If response is not JSON
                    logger.debug(f"Response text for {city['city_code']}: {response.text}")
                    print(f"Response text for {city['city_code']}: {response.text}")
            proxies.remove(proxy)  # Remove faulty proxy
        except requests.exceptions.RequestException as e:
            logger.error(f"Request exception for city {city['city_code']}: {e}")
            print(f"Request exception for {city['city_code']}: {e}")
            proxies.remove(proxy)  # Remove faulty proxy
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
    """
    Saves fetched data to a file.
    Args:
        directory_name (str): Directory to save the data.
        city_code (str): Code of the city, used for filename.
        data (dict or str): Data to save.
    """
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

def refresh_proxies(proxies_container, interval=3600):
    """
    Refreshes the proxy pool at regular intervals.
    Args:
        proxies_container (dict): A dictionary to store proxies.
        interval (int): Refresh interval in seconds.
    """
    def refresh():
        while True:
            print("Refreshing proxies...")
            new_proxies = fetch_proxies_from_multiple_sources()
            if new_proxies:
                valid_proxies = get_valid_proxies(new_proxies)
                if valid_proxies:
                    proxies_container['proxies'] = valid_proxies
                    logger.info(f"Proxy pool refreshed with {len(valid_proxies)} proxies.")
                    print(f"Proxy pool refreshed with {len(valid_proxies)} proxies.")
                else:
                    logger.warning("No valid proxies found during refresh.")
                    print("No valid proxies found during refresh.")
            else:
                logger.warning("No proxies fetched during refresh.")
                print("No proxies fetched during refresh.")
            time.sleep(interval)
    
    thread = threading.Thread(target=refresh, daemon=True)
    thread.start()

def fetch_and_save_all_cities_parallel():
    """
    Orchestrates the fetching and saving of data for all cities using proxies.
    """
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

    # Fetch proxies from multiple sources
    proxy_list = fetch_proxies_from_multiple_sources()
    if not proxy_list:
        logger.critical("No proxies fetched. Exiting script.")
        print("Critical Error: No proxies fetched. Exiting script.")
        return

    # Validate proxies
    valid_proxies = get_valid_proxies(proxy_list)
    if not valid_proxies:
        logger.critical("No valid proxies available after validation. Exiting script.")
        print("Critical Error: No valid proxies available after validation. Exiting script.")
        return

    # Initialize proxy pool container
    proxies_container = {'proxies': valid_proxies}

    # Start proxy refreshing in the background
    refresh_proxies(proxies_container, interval=3600)  # Refresh every hour

    # Define the number of worker threads
    max_workers = min(10, len(cities))  # Adjust based on your needs
    logger.debug(f"Using {max_workers} worker threads for fetching data.")
    print(f"Starting data fetch with {max_workers} worker threads.")

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all fetch tasks
        future_to_city = {
            executor.submit(fetch_data_for_city, city, proxies_container['proxies']): city
            for city in cities
        }
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
