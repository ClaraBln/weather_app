from dotenv import load_dotenv
from datetime import datetime
import os
import requests
import streamlit as st
import pandas as pd


load_dotenv()  # Load the content of .env into the environnement 

class WeatherRequest():
    api_key = os.getenv('api_weather')
    
    def __init__(self, city_name, country_code):
        self.city_name = city_name
        self.country_code = country_code
    
    def get_coordinate(self):
        if not self.__class__.api_key:
            st.error("API key is missing.")
            return None
        try:
            r_coordinate = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={self.city_name},{self.country_code}&appid={self.__class__.api_key}', timeout=2)
        except requests.exceptions.Timeout:
            st.error("Sorry, the server is taking too long")
            return None
        except Exception as e:
            st.error(f"Connection error: {e}")
            return None
        if r_coordinate.status_code == 401:
            st.error("API key is invalid or unauthorized.")
            return None
        elif r_coordinate.status_code == 200:
            result = r_coordinate.json()
            if not result:
                st.error("City not found. Please check the name and country code.")
                return None
            lat = result[0]['lat']
            lon = result[0]['lon']
            if lat is None or lon is None:
                st.error("Latitude/Longitude not found in API response.")
                return None
            return lat, lon
        else:
            st.error(f"Unexpected error: {r_coordinate.status_code}")
            return None
    
    def get_weather(self):
        lat, lon = self.get_coordinate()
        if lat is None or lon is None:
            return None
        try:
            r_weather = requests.get(f'https://api.openweathermap.org/data/3.0/onecall?lat={lat}&lon={lon}&units=metric&appid={self.__class__.api_key}', timeout=2)
        except requests.exceptions.Timeout:
            st.error("Sorry, the server is taking too long.")
            return None
        except Exception as e:
            st.error(f"Weather API connection error: {e}")
            return None
        if r_weather.status_code == 401:
            st.error("API key is invalid or unauthorized for weather.")
            return None
        elif r_weather.status_code == 200:
            data = r_weather.json()
            try:
                temp = data['current']['temp']
                feels_temp = data['current']['feels_like']
                humidity = data['current']['humidity']
                weather_desc = data['current']['weather'][0]['description']
                icon_code = data['current']['weather'][0]['icon']
                min_temp = data['daily'][0]['temp']['min']
                max_temp = data['daily'][0]['temp']['max']
                return temp, feels_temp, humidity, weather_desc, icon_code, min_temp, max_temp
            except (KeyError, IndexError):
                st.error("Incomplete weather data received.")
                return None
        else:
            st.error(f"Unexpected error from weather: {r_weather.status_code}")
            return None

    def get_daily_forecast(self):
        lat, lon = self.get_coordinate()
        if lat is None or lon is None:
            return None
        try:
            r_forecast = requests.get(f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={self.__class__.api_key}', timeout=2)
        except requests.exceptions.Timeout:
            st.error("Sorry, the server is taking too long.")
            return None
        except Exception as e:
            st.error(f"Weather API connection error: {e}")
            return None
        if r_forecast.status_code == 401:
            st.error("API key is invalid or unauthorized for forecast.")
            return None
        elif r_forecast.status_code == 200:
            data_forcast = r_forecast.json()['list']
            forecasts_by_day = {}
            for entry in data_forcast:
                dt = datetime.fromtimestamp(entry["dt"])
                day = dt.date()
                hour = dt.hour
                if day not in forecasts_by_day or abs(hour-12) < abs(forecasts_by_day[day]["hour"]-12):
                    forecasts_by_day[day] = {"entry": entry, "hour": hour}
            final_forecast = []
            for days in sorted(forecasts_by_day.keys())[:5]:
                e = forecasts_by_day[days]["entry"]
                final_forecast.append({
                "date": days.strftime("%d/%m"),
                "min": e["main"]["temp_min"],
                "max": e["main"]["temp_max"],
                "desc": e["weather"][0]["description"].capitalize(),
                "icon": e["weather"][0]["icon"] })
        return final_forecast


class MapRequest:
    api_key = os.getenv('api_map')
    
    def __init__(self, weather_request):
        self.weather_request = weather_request
    
    def get_coords(self):
        coords = self.weather_request.get_coordinate()
        if coords:
            latitude, longitude = coords
            return latitude, longitude
        else :
            st.error("Unsuccesful coordinate retrival")
            return None, None
        
    def get_map(self):
        latitude, longitude = self.get_coords()
        if not self.__class__.api_key:
            st.error("API key is missing")
            return
        map_html = f"""
            <iframe
                width="700"
                height="450"
                style="border:0"
                loading="lazy"
                allowfullscreen
                referrerpolicy="no-referrer-when-downgrade"
                src="https://www.google.com/maps/embed/v1/view?key={self.api_key}&center={latitude},{longitude}&zoom=13">
            </iframe>
        """
        st.components.v1.html(map_html, height=450)
        
        
       
def display_data_current():
    weather_request = WeatherRequest(city,country)
    temp, feels_temp, humidity, weather_desc, icon_code, min_temp, max_temp = weather_request.get_weather()
    map_request = MapRequest(weather_request)
    cols = st.columns(2)
    cols[0].write(f'**Location:** :blue[{city.capitalize()}, {country.capitalize()}]')
    cols[0].write(f'**Temperature:** :blue[{temp}°C]')
    cols[0].write(f'**Feels like:** :blue[{feels_temp}°C]')
    cols[0].write(f'**Humidity:** :blue[{humidity}%]')
    cols[0].write(f'**Minimum temperature:** :blue[{min_temp}°C]')
    cols[0].write(f'**Maximum temperature:** :blue[{max_temp}°C]')
    icon_url = f"https://openweathermap.org/img/wn/{icon_code}@2x.png"
    cols[1].write(f'**Weather description:**')
    cols[1].image(icon_url, caption=weather_desc.capitalize())
    map_request.get_map()
    
def display_data_forcast():
    forecast_request = WeatherRequest(city,country)
    forecast = forecast_request.get_daily_forecast()
    if not forecast:
        st.error("No forecast found.")
        return
    st.write(f'**Location:** :blue[{city.capitalize()}, {country.capitalize()}]')
    header_cols = st.columns([1.5, 2.5, 3])
    header_cols[0].markdown("**Date**")
    header_cols[1].markdown("**Weather Description**")
    header_cols[2].markdown("**Temperatures**")
    for prevision in forecast:
        columns = st.columns([1.5, 2.5, 3])
        columns[0].write(f"**{prevision['date']}**")
        icon_url = f"https://openweathermap.org/img/wn/{prevision['icon']}@2x.png"
        columns[1].image(icon_url, width=70, caption=prevision['desc'])
        columns[2].write(f"Min: :blue[{prevision['min']}°C] / Max: :blue[{prevision['max']}°C]")
    
        
def main():
    global city, country
    
    st.header("Weather application", divider=True)
    st.markdown("## Get the weather condition anywhere you desire")
    
    col = st.columns(2)
    city = col[0].text_input('Name of the city you want to look up: ')
    country = col[1].text_input('Corresponding two-digit country code: ')
    st.write(f'You can find the official country code following the ISO 3166 at: https://www.iso.org/obp/ui/#search')
    
    if st.button('Search'):
        tab1, tab2 = st.tabs(['Current weather', 'Forcast for 5 days'])
        with tab1:
            st.header('Current weather conditions')
            display_data_current()
        with tab2:
            st.header('Forcast for 5 days at 12pm')
            display_data_forcast()
    

if __name__ == '__main__':
    main()
