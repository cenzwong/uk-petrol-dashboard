import streamlit as st
import pandas as pd
from streamlit_geolocation import streamlit_geolocation
from geopy.distance import geodesic

# URL of the CSV file
url = "https://raw.githubusercontent.com/cenzwong/uk-petrol-ingestion/refs/heads/main/data/shell/shell_fuel_prices_2025-04-15.csv"

# Read the CSV file from the URL
df = pd.read_csv(url)


# App title
st.title('Shell Petrol Price Finder')

# Show when the data was last updated
last_updated = df['last_updated'].max()
st.markdown(f"**Data last updated:** {last_updated}")

# Sidebar: get user's geolocation
st.sidebar.header('Filter by Location')
st.sidebar.markdown("Please allow location access in your browser.")

# Let user set the radius in miles
radius_miles = st.sidebar.slider("🔍 Search radius (miles):", min_value=1, max_value=20, value=3)
radius_km = radius_miles * 1.60934

# Call geolocation
location = streamlit_geolocation()
st.sidebar.write("📍 Your current location:", location)

if location and location.get('latitude') and location.get('longitude'):
    user_lat = location['latitude']
    user_lon = location['longitude']

    # Compute distance and filter within user-defined radius
    def within_radius(row):
        return geodesic((user_lat, user_lon), (row['lat'], row['lon'])).km <= radius_km

    shell_df = df[df['brand'].str.lower() == 'shell']
    filtered_df = shell_df[shell_df.apply(within_radius, axis=1)]

    st.success(f"Filtering Shell stations within ~{radius_miles} miles of: {user_lat}, {user_lon}")

    # Display the filtered table with E10 and B7 prices
    st.subheader('Filtered Shell Petrol Stations')
    st.dataframe(filtered_df[['site_id', 'brand', 'address', 'postcode', 'lat', 'lon', 'E10', 'B7']])

else:
    st.sidebar.info("📍 Waiting for your location... Please allow location access in your browser.")
