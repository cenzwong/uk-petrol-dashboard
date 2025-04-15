import requests
from datetime import date

# Get today's date in YYYY-MM-DD format
today_str = date.today().isoformat()

# URL to download
url = "https://www.shell.co.uk/fuel-prices-data.html"
response = requests.get(url)

# Create filename with today's date
filename = f"./data/shell/shell_fuel_prices_{today_str}.json"

# Write to file
with open(filename, "wb") as file:
    file.write(response.content)

print(f"Download complete: {filename}")
