import requests
import logging


def fetch_proxies():
    """
    Fetches a list of HTTPS proxies from ProxyScrape.
    Returns:
        List of proxy strings in the format 'ip:port'.
    """
    proxy_api_url = (
        "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=https&timeout=10000&"
        "country=all&ssl=yes&anonymity=all"
    )
    
    try:
        response = requests.get(proxy_api_url, timeout=30)
        response.raise_for_status()
        
        proxies = response.text.split('\n')
        # Remove any empty strings
        proxies = [proxy.strip() for proxy in proxies if proxy.strip()]
        
        logger.debug(f"Fetched {len(proxies)} proxies from ProxyScrape.")
        print(f"Fetched {len(proxies)} proxies from ProxyScrape.")
        return proxies
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching proxies from ProxyScrape: {e}")
        print(f"Error fetching proxies from ProxyScrape: {e}")
        return []
    