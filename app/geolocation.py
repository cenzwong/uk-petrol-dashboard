import streamlit.components.v1 as components

def get_geolocation():
    geolocation_js = """
    <script>
    navigator.geolocation.getCurrentPosition(
        (position) => {
            const latitude = position.coords.latitude;
            const longitude = position.coords.longitude;
            const data = {lat: latitude, lon: longitude};
            window.parent.postMessage(JSON.stringify(data), "*");
        },
        (err) => {
            const data = {lat: null, lon: null, error: err.message};
            window.parent.postMessage(JSON.stringify(data), "*");
        }
    );
    </script>
    """
    components.html(geolocation_js, height=0)
