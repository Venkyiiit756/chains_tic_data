from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

# Set up Chrome options
chrome_options = Options()
chrome_options.binary_location = "/usr/bin/chromium-browser"  # Specify the path to the Chromium binary
chrome_options.add_argument("--headless")  # Run headless Chromium
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model
chrome_options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource issues
chrome_options.add_argument("--disable-gpu")  # Disable GPU for headless environments
chrome_options.add_argument("--remote-debugging-port=9222")  # Enable remote debugging
chrome_options.add_argument("--disable-software-rasterizer")


# Set up Selenium WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Define the URL
url = "https://api_new.cinepolisindia.com/api/movies/show-times/HO00015515/?request_type=get-show-times&show_date=2024-09-07&movie_id=HO00015515&city_id=35&experience=&isVip=N"

# Load the URL
driver.get(url)

# Get the page source or look for the data in the network responses
page_source = driver.page_source
print(page_source)

# Close the browser
driver.quit()
