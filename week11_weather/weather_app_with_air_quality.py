"""
TRAVEL WEATHER TOOL - AI Masterclass Day 3
How to run:
1. pip install requests python-dotenv
2. Create .env file with OPENWEATHER_API_KEY=your_key
3. python week11/day3_travel_info.py
4. Enter any city/district e.g. Mbarara, Gulu, Kampala, Nairobi, London

What it does:
- Takes user input (city name) - not hardcoded
- Makes 3 API calls: OpenWeather Current + OpenWeather Forecast + World Bank Country Info
- Combines results into one readable report + saves to JSON
"""

import requests
import json
from datetime import datetime

API_KEY = "fde104393d9a1b3a4945b58f5dfa7336"

# ---------------- CURRENT WEATHER ----------------
def get_current_weather(city):
    url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        print(f"Error: {data.get('message', 'City not found')}")
        return None

    return data

# ---------------- 5-DAY FORECAST ----------------
def get_forecast(city):
    url = f"http://api.openweathermap.org/data/2.5/forecast?q={city}&appid={API_KEY}&units=metric"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return None
    return data

# ---------------- COUNTRY INFO ----------------
def get_country_info(country_code):
    try:
        url = f"https://restcountries.com/v3.1/alpha/{country_code}"
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            return None
        data = response.json()
        # Sometimes API returns a dict with error, not a list
        if isinstance(data, dict):
            return None
        if not data:
            return None
        item = data[0]
        return {
            "country": item["name"]["common"],
            "region": item.get("region", "N/A"),
            "capital": (item.get("capital") or ["N/A"])[0]
        }
    except Exception as e:
        print(f"Country info failed: {e}")
        return None

# ---------------- AIR QUALITY - NEW ----------------
def get_air_quality(lat, lon):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={API_KEY}"
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return None

    item = data["list"][0]
    aqi = item["main"]["aqi"]
    components = item["components"]

    # AQI meaning from OpenWeatherMap
    aqi_meaning = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor"
    }

    return {
        "aqi": aqi,
        "meaning": aqi_meaning.get(aqi, "Unknown"),
        "pm2_5": components.get("pm2_5"),
        "pm10": components.get("pm10"),
        "co": components.get("co"),
        "no2": components.get("no2"),
        "o3": components.get("o3")
    }

# ---------------- MAIN TOOL ----------------
def run_tool():
    city = input("Enter city (e.g. Parombo): ").strip()
    if not city:
        city = "Parombo"

    weather = get_current_weather(city)
    if not weather:
        return

    country_code = weather["sys"]["country"]
    lat = weather["coord"]["lat"]
    lon = weather["coord"]["lon"]

    forecast = get_forecast(city)
    country = get_country_info(country_code)
    air = get_air_quality(lat, lon)

    # --- PRINT CURRENT WEATHER ---
    print(f"\n--- CURRENT WEATHER in {weather['name']}, {country_code} ---")
    print(f"Temperature: {weather['main']['temp']}°C (feels like {weather['main']['feels_like']}°C)")
    print(f"Condition: {weather['weather'][0]['description'].title()}")
    print(f"Humidity: {weather['main']['humidity']}% | Wind: {weather['wind']['speed']} m/s")

    # --- PRINT COUNTRY ---
    if country:
        print(f"\n--- ABOUT {country_code} ---")
        print(f"Country: {country['country']}")
        print(f"Region: {country['region']}")
        print(f"Capital: {country['capital']}")

    # --- PRINT AIR QUALITY ---
    if air:
        print(f"\n--- AIR QUALITY in {weather['name']} ---")
        print(f"AQI: {air['aqi']} - {air['meaning']}")
        print(f"PM2.5: {air['pm2_5']} µg/m³ | PM10: {air['pm10']} µg/m³")
        print(f"CO: {air['co']} µg/m³ | NO2: {air['no2']} µg/m³ | O3: {air['o3']} µg/m³")

    # --- PRINT 5-DAY PREDICTION ---
    if forecast:
        print(f"\n--- 5-DAY PREDICTION for {weather['name']} ---")
        seen_dates = set()
        for item in forecast["list"]:
            date = datetime.fromtimestamp(item["dt"]).strftime("%a %d %b")
            if date not in seen_dates:
                seen_dates.add(date)
                temp_min = item["main"]["temp_min"]
                temp_max = item["main"]["temp_max"]
                cond = item["weather"][0]["description"].title()
                print(f"{date}: {temp_min:.0f}°C - {temp_max:.0f}°C | {cond}")
            if len(seen_dates) >= 5:
                break

    # --- SAVE REPORT ---
    report = {
        "city": weather["name"],
        "country_code": country_code,
        "current": weather["main"],
        "country_info": country,
        "air_quality": air,
        "forecast_raw": forecast
    }
    filename = f"{weather['name'].lower()}_weather_report.json"
    with open(filename, "w") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved to {filename} ✅")

if __name__ == "__main__":
    run_tool()