const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ headless: true });
  const page = await browser.newPage();

  // Set a User-Agent and other headers to mimic real browser behavior
  await page.setUserAgent('Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36');
  
  // Add additional headers like Accept and Referer
  await page.setExtraHTTPHeaders({
    'Accept': 'application/json, text/plain, */*',
    'Referer': 'https://cinepolisindia.com',
    'Accept-Language': 'en-US,en;q=0.9',
  });

  // Navigate to the page to get cookies (Cloudflare, etc.)
  const apiUrl = 'https://api_new.cinepolisindia.com/api/movies/show-times/HO00015515/?request_type=get-show-times&show_date=2024-09-07&movie_id=HO00015515&city_id=35&experience=&isVip=N';

  try {
    // Navigate to the page to let Puppeteer solve any Cloudflare challenge
    await page.goto('https://cinepolisindia.com', { waitUntil: 'networkidle2' });

    // Extract the cookies set after Cloudflare challenge
    const cookies = await page.cookies();

    // Format the cookies into a string that can be sent in headers
    const cookieString = cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');

    // Now, use these cookies and headers to access the API directly
    await page.setCookie(...cookies);
    
    // Try accessing the API with the cookies and headers
    const response = await page.goto(apiUrl, { waitUntil: 'networkidle0' });

   if (response.status() === 200) {
       const jsonResponse = await response.json();
       console.log('API Response:', JSON.stringify(jsonResponse, null, 2)); // Pretty-print the full JSON response
   } else {
      console.error('Failed to load API. Status:', response.status());
    }

  } catch (error) {
    console.error('Error:', error);
  }

  await browser.close();
})();
