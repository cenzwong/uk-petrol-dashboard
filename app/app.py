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

# Call geolocation
location = streamlit_geolocation()

# Notify user about geolocation status
if location and location.get('latitude') and location.get('longitude'):
    st.success(f"📍 Location detected: ({location['latitude']:.5f}, {location['longitude']:.5f})")
else:
    st.info("📍 Location not available yet. Please allow location access in your browser.")

# Location and radius filtering section
st.markdown("### 🔍 Filter by Location")

# Let user set the radius in miles, including option for 'All'
radius_options = list(range(1, 21)) + ["All"]
radius_selection = st.selectbox("Search radius (miles):", radius_options, index=2)

if location and location.get('latitude') and location.get('longitude'):
    user_lat = location['latitude']
    user_lon = location['longitude']

    # User-defined filters
    st.markdown("### 🛠️ Additional Filters")

    all_brands = df['brand'].dropna().unique().tolist()
    brand_filter = st.multiselect("Select brand(s):", options=all_brands, default=[b for b in all_brands if b.lower() == "shell"])

    # Multiselect-like input for postcodes
    postcode_input = st.text_input("Enter partial postcode(s) separated by commas (e.g. HA, HP):")
    sort_by_price = st.radio("Sort by price:", options=["None", "E10 (asc)", "E10 (desc)", "B7 (asc)", "B7 (desc)"], horizontal=True)

    # Filter dataframe based on brand filter (case insensitive)
    location_df = df[df['brand'].str.lower().isin([b.lower() for b in brand_filter])]

    if radius_selection == "All":
        filtered_df = location_df.copy()
        st.success(f"Showing all selected stations (ignoring location filter)")
    else:
        radius_km = int(radius_selection) * 1.60934

        # Compute distance and filter within user-defined radius
        def within_radius(row):
            return geodesic((user_lat, user_lon), (row['lat'], row['lon'])).km <= radius_km

        filtered_df = location_df[location_df.apply(within_radius, axis=1)]

        st.success(f"Filtering stations within ~{radius_selection} miles of: {user_lat}, {user_lon}")

    # Apply postcode filter
    if postcode_input:
        postcode_parts = [p.strip().upper() for p in postcode_input.split(',') if p.strip()]
        filtered_df = filtered_df[filtered_df['postcode'].str.upper().str.startswith(tuple(postcode_parts))]

    # Apply sorting
    if sort_by_price != "None":
        price_col, direction = sort_by_price.split(" (")
        ascending = direction.strip(")") == "asc"
        filtered_df = filtered_df.sort_values(by=price_col, ascending=ascending)

    # Display the filtered table with E10 and B7 prices
    st.subheader('Filtered Petrol Stations')
    st.dataframe(filtered_df[['site_id', 'brand', 'address', 'postcode', 'lat', 'lon', 'E10', 'B7']])

    # E10 Price Analysis Section
    st.subheader("E10 Price Analysis")
    e10_data = filtered_df[['E10', 'postcode']].dropna()

    if not e10_data.empty:
        mean_price = e10_data['E10'].mean()
        std_price = e10_data['E10'].std()
        min_price = e10_data['E10'].min()
        max_price = e10_data['E10'].max()

        # Stats cards
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Mean (£)", f"{mean_price:.2f}")
        col2.metric("Std Dev (£)", f"{std_price:.2f}")
        col3.metric("Min (£)", f"{min_price:.2f}")
        col4.metric("Max (£)", f"{max_price:.2f}")

        # Two plots side by side
        col_hist, col_box = st.columns(2)

        # Histogram with KDE using Plotly (no zoom)
        with col_hist:
            st.markdown("**📊 E10 Price Distribution**")
            fig_hist = px.histogram(e10_data, x='E10', nbins=20, title="E10 Price Distribution",
                                    labels={"E10": "E10 Price (£)"}, marginal="rug", opacity=0.75)
            fig_hist.update_layout(dragmode=False)
            st.plotly_chart(fig_hist, use_container_width=True)

        # Boxplot using Plotly with postcode in hover info (no zoom)
        with col_box:
            st.markdown("**📦 E10 Price Boxplot**")
            fig_box = go.Figure()
            fig_box.add_trace(go.Box(
                x=e10_data['E10'],
                text=e10_data['postcode'],
                hoverinfo='x+text',
                name="E10 Prices",
                marker_color="lightgreen"
            ))
            fig_box.update_layout(
                title="Boxplot of E10 Prices",
                xaxis_title="E10 Price (£)",
                dragmode=False
            )
            st.plotly_chart(fig_box, use_container_width=True)
    else:
        st.warning("No valid E10 price data available to display.")
else:
    st.info("📍 Waiting for your location... Please allow location access in your browser.")
