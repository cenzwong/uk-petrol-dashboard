import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
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

    # E10 Price Analysis Section
    st.subheader("E10 Price Analysis")
    e10_prices = filtered_df['E10'].dropna()

    if not e10_prices.empty:
        mean_price = e10_prices.mean()
        std_price = e10_prices.std()
        min_price = e10_prices.min()
        max_price = e10_prices.max()

        # Stats cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean (£)", f"{mean_price:.2f}")
        col2.metric("Std Dev (£)", f"{std_price:.2f}")
        col3.metric("Min (£)", f"{min_price:.2f}")
        col4.metric("Max (£)", f"{max_price:.2f}")

        # Histogram with KDE using Plotly
        st.markdown("**📊 E10 Price Distribution**")
        fig_hist = px.histogram(e10_prices, nbins=20, title="E10 Price Distribution",
                                labels={"value": "E10 Price (£)"},
                                marginal="rug", opacity=0.75)
        st.plotly_chart(fig_hist, use_container_width=True)

        # Boxplot using Plotly
        st.markdown("**📦 E10 Price Boxplot**")
        fig_box = go.Figure()
        fig_box.add_trace(go.Box(x=e10_prices, name="E10 Prices", marker_color="lightgreen"))
        fig_box.update_layout(title="Boxplot of E10 Prices", xaxis_title="E10 Price (£)")
        st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.warning("No valid E10 price data available to display.")
else:
    st.sidebar.info("📍 Waiting for your location... Please allow location access in your browser.")
