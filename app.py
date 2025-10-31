import streamlit as st #type: ignore
import requests #type: ignore
import datetime as dt 
import plotly.express as px #type: ignore
import pandas as pd #type: ignore
import geocoder #type: ignore
import base64
import time
import os
from dotenv import load_dotenv #type: ignore
load_dotenv()
API_KEY = os.getenv("API_KEY")

def load_svg(path):
    with open(path, "r", encoding="utf-8") as file:
        svg = file.read()
    b64 = base64.b64encode(svg.encode("utf-8")).decode("utf-8")
    return f"data:image/svg+xml;base64,{b64}"

SVG_WEATHER = load_svg("weather-svgrepo-com.svg")
SVG_FORECAST = load_svg("location.svg")
SVG_TREND = load_svg("forecast.svg")
SVG_INSIGHT = load_svg("forecast.svg")
SVG_ALERT = load_svg("alert.svg")

st.set_page_config(page_title="Smart Weather Predictor", page_icon=SVG_WEATHER, layout="wide")

st.markdown("""
    <style>
    body {
        background-color: #f7f9fc;
        font-family: 'Poppins', sans-serif;
    }
    .main {
        background: linear-gradient(135deg, #eef2f3 0%, #8e9eab 100%);
        padding: 25px;
        border-radius: 12px;
        box-shadow: 0 6px 14px rgba(0,0,0,0.1);
    }
    h1, h2, h3 {
        color: #1a1a1a;
    }
    .metric-card {
        padding: 15px;
        border-radius: 10px;
        background-color: white;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        text-align: center;
    }
    .alert-card {
        padding: 10px;
        border-radius: 8px;
        color: white;
        margin: 5px 0;
        font-weight: 500;
    }
    .footer {
        text-align: center;
        font-size: 13px;
        color: #555;
        padding-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

st.sidebar.image(SVG_WEATHER, width=80)
st.sidebar.title("Settings")
auto_detect = st.sidebar.checkbox("Auto Detect Location", value=True)
refresh_rate = st.sidebar.slider("Auto Refresh (minutes)", 1, 15, 10)

if auto_detect:
    g = geocoder.ip('me')
    detected_city = g.city if g.city else "Visakhapatnam"
    st.sidebar.success(f"Detected: {detected_city}")
else:
    detected_city = None
cities = [
    "Visakhapatnam", "Vijayawada", "Hyderabad", "Chennai", "Bengaluru", "Mumbai",
    "Pune", "Delhi", "Kolkata", "Ahmedabad", "Surat", "Jaipur", "Lucknow",
    "Kanpur", "Nagpur", "Indore", "Bhopal", "Coimbatore", "Madurai", "Tirupati",
    "Mysuru", "Mangalore", "Kochi", "Thiruvananthapuram", "Patna", "Chandigarh",
    "Bhubaneswar", "Ranchi", "Raipur", "Guwahati", "New York", "London", "Paris",
    "Tokyo", "Dubai", "Sydney", "Singapore", "Toronto", "Berlin", "Cape Town"
]

city = st.sidebar.selectbox("Select City", cities, index=0)
if detected_city:
    city = detected_city

st.markdown(f"<img src='{SVG_WEATHER}' width='70'>", unsafe_allow_html=True)
st.title("Smart Weather Predictor")
st.write("Get real-time weather updates, 5-day forecasts, visual insights, and smart alerts.")

if "last_city" not in st.session_state:
    st.session_state["last_city"] = city

def get_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}"
    r = requests.get(url).json()
    if r.get("cod") != 200:
        return None
    return {
        "city": r["name"],
        "temperature": round(r["main"]["temp"] - 273.15, 2),
        "feels_like": round(r["main"]["feels_like"] - 273.15, 2),
        "humidity": r["main"]["humidity"],
        "pressure": r["main"]["pressure"],
        "wind_speed": r["wind"]["speed"],
        "weather": r["weather"][0]["description"]
    }

def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}"
    return requests.get(url).json()

if st.button("Get Weather"):
    weather = get_weather(city)
    if not weather:
        st.error("City not found or API issue.")
    else:
        st.markdown(f"<img src='{SVG_FORECAST}' width='45'>", unsafe_allow_html=True)
        st.subheader(f"{weather['city']} {weather['weather'].title()}")

        desc = weather["weather"].lower()
        col1, col2, col3 = st.columns(3)
        with col1: st.metric("Temperature (°C)", weather["temperature"])
        with col2: st.metric("Feels Like (°C)", weather["feels_like"])
        with col3: st.metric("Humidity (%)", weather["humidity"])
        col4, col5 = st.columns(2)
        with col4: st.metric("Pressure (hPa)", weather["pressure"])
        with col5: st.metric("Wind Speed (m/s)", weather["wind_speed"])
        st.markdown("</div>", unsafe_allow_html=True)

        # Alerts
        st.markdown(f"<img src='{SVG_ALERT}' width='45'>", unsafe_allow_html=True)
        st.subheader("Weather Alerts")
        if "rain" in desc:
            st.markdown("<div class='alert-card' style='background-color:#4a90e2;'>Rain expected — carry an umbrella!</div>", unsafe_allow_html=True)
        elif weather["temperature"] > 35:
            st.markdown("<div class='alert-card' style='background-color:#e74c3c;'>Heatwave Alert: Stay hydrated and avoid peak sunlight.</div>", unsafe_allow_html=True)
        elif weather["temperature"] < 15:
            st.markdown("<div class='alert-card' style='background-color:#3498db;'>Cold weather — keep warm and carry a jacket.</div>", unsafe_allow_html=True)
        elif "haze" in desc or "fog" in desc:
            st.markdown("<div class='alert-card' style='background-color:#95a5a6;'>Low visibility, drive safely.</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='alert-card' style='background-color:#27ae60;'>Pleasant weather today!</div>", unsafe_allow_html=True)
        forecast_data = get_forecast(city)
        if forecast_data.get("cod") == "200":
            st.markdown(f"<img src='{SVG_TREND}' width='45'>", unsafe_allow_html=True)
            st.subheader("5-Day Temperature Forecast")
            daily_temps = {}
            for entry in forecast_data["list"]:
                date = dt.datetime.fromtimestamp(entry["dt"]).strftime("%Y-%m-%d")
                temp_c = entry["main"]["temp"] - 273.15
                daily_temps.setdefault(date, []).append(temp_c)
            avg_temps = {d: sum(t) / len(t) for d, t in daily_temps.items()}
            st.line_chart(avg_temps)
            dates, temps, humidities = [], [], []
            for entry in forecast_data["list"]:
                date = dt.datetime.fromtimestamp(entry["dt"])
                temps.append(entry["main"]["temp"] - 273.15)
                humidities.append(entry["main"]["humidity"])
                dates.append(date)

            temp_chart = px.line(x=dates, y=temps, title="Temperature Trend (Next 5 Days)",
                                 labels={'x': 'Date', 'y': 'Temperature (°C)'})
            st.plotly_chart(temp_chart, use_container_width=True)
            humidity_chart = px.line(x=dates, y=humidities, title="Humidity Trend (Next 5 Days)",
                                     labels={'x': 'Date', 'y': 'Humidity (%)'})
            st.plotly_chart(humidity_chart, use_container_width=True)
            st.markdown(f"<img src='{SVG_INSIGHT}' width='45'>", unsafe_allow_html=True)
            st.subheader("Smart Weather Insights")
            avg_temp = sum(temps) / len(temps)
            avg_humidity = sum(humidities) / len(humidities)
            if avg_temp > 30:
                st.info("Hot Week Ahead: Stay hydrated and avoid going out during afternoons.")
            elif avg_temp < 20:
                st.info("Cool Week: Ideal for outdoor walks, but keep warm.")
            else:
                st.info("Pleasant Weather Ahead: Perfect for travel and activities.")
            if avg_humidity > 80:
                st.warning("High Humidity: Expect sticky air, stay cool.")
            elif avg_humidity < 40:
                st.info("Dry Conditions: Use moisturizer or humidifier indoors.")

            # CSV download
            df = pd.DataFrame({
                "Date": [d.strftime("%Y-%m-%d %H:%M") for d in dates],
                "Temperature (°C)": temps,
                "Humidity (%)": humidities
            })
            csv = df.to_csv(index=False).encode("utf-8")
            st.download_button("Download Forecast Data (CSV)", csv, f"{city}_forecast.csv", "text/csv")

        st.session_state["last_city"] = city

st.sidebar.markdown("---")
st.sidebar.info(f"Last searched: {st.session_state['last_city']}")
st.sidebar.caption("Developed by **Harsha Teja**")

st.markdown("<div class='footer'>© 2025 Smart Weather Predictor | Powered by OpenWeatherMap & Streamlit</div>", unsafe_allow_html=True)
