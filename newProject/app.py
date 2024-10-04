from flask import Flask, render_template
from fetch_showtimes import fetch_showtimes

# Fetch data for a specific city
city_code = 'WAR'
city_name = 'WAR'
print(f"Fetching data for city: {city_name}")
df = fetch_showtimes(city_code, city_name)
print(f"Data fetching completed for city: {city_name}")

# Step 2: Display as a visually appealing webpage using Flask
app = Flask(__name__)

@app.route('/')
def home():
    print("Rendering home page...")
    # Convert the DataFrame to HTML
    html_table = df.to_html(classes='table table-striped table-hover table-bordered', index=False)
    print("DataFrame converted to HTML table.")
    
    # Render the HTML template with the data
    return render_template('home.html', html_table=html_table)

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0')
