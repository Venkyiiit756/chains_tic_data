from playwright.sync_api import sync_playwright

def url_config():
    movie_id = "HO00015515"
    date = "2024-09-07"
    city_id = "35"
    experience = ""
    isVip = "N"
    config_api_url = f"https://api_new.cinepolisindia.com/api/movies/show-times/{movie_id}/?request_type=get-show-times&show_date={date}&movie_id={movie_id}&city_id={city_id}&experience={experience}&isVip={isVip}/"
    return config_api_url

def get_cinepolis_show_times():
    api_url = url_config()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)  # Launch browser in headless mode
        user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        context = browser.new_context(
           user_agent=user_agent  # Apply the User-Agent
        )
        page = context.new_page()  # Create a new page in the browser
        
        # Visit the main site to initiate session and load cookies
        page.goto("https://www.cinepolisindia.com")
        page.wait_for_load_state("networkidle")  # Wait for the network to be idle
        
        # Now fetch the API data using the session details
        response = page.request.get(api_url)
        
        if response.status == 200:
            print(response.json())  # Output the JSON response
        else:
            print(f"Error fetching data: {response.status}")
            print(response.text())
        
        # Close the browser once done
        browser.close()

get_cinepolis_show_times()
