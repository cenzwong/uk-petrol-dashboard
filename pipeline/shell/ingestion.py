import pandas as pd
import json
from datetime import date


def get_data() -> pd.DataFrame:
    # Get today's date
    today_str = date.today().isoformat()

    # File path
    json_path = f"data/shell/shell_fuel_prices_{today_str}.json"

    # Read JSON file
    with open(json_path, 'r') as file:
        data = json.load(file)

    # Normalize JSON data
    df = pd.json_normalize(data, record_path=['stations'], meta=['last_updated'])

    # Select and rename columns
    df_unpacked = df[['last_updated', 'site_id', 'brand', 'address', 'postcode', 'location.latitude', 'location.longitude', 'prices.B7', 'prices.E10']]
    df_unpacked.columns = ['last_updated', 'site_id', 'brand', 'address', 'postcode', 'lat', 'lon', 'B7', 'E10']

    return df_unpacked

if __name__ == "__main__":
    print(get_data().head())
