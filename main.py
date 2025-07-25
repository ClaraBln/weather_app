from dotenv import load_dotenv
import os
import requests
import streamlit as st


load_dotenv()  # Load the content of .env into the environement 

class Request_weather():
    api_key = os.getenv('api_key')
    
    def __init__(self, city_name, country_code):
        self.city_name = city_name
        self.country_code = country_code
    
    def get_coordinate(self):
        try:
            r_coordinate = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={self.city_name},{self.country_code}&appid={self.__class__.api_key}', timeout=2)
        except requests.exceptions.Timeout:
            print("Sorry, the server is taking too long")
        else:
            if r_coordinate.status_code == 200 :
                result = r_coordinate.json()
                lat = result[0]['lat']
                lon = result[0]['lon']
                return [lat, lon]
            else:
                st.error("City not found or API key error")
    
    def get_weather(self):
        necessary_data = self.get_coordinate()
        try:
            r_weather = requests.get(f'https://api.openweathermap.org/data/3.0/onecall?lat={necessary_data[0]}&lon={necessary_data[1]}&exclude=hourly,daily&units=metric&appid={self.__class__.api_key}', timeout=2)
        except requests.exceptions.Timeout:
            print("Sorry, the server is taking too long")
        else: 
            if r_weather.status_code == 200 :
                data = r_weather.json()
                temp = data['current']['temp']
                feels_temp = data['current']['feels_like']
                weather_desc = data['current']['weather'][0]['description']
                icon_code = data['current']['weather'][0]['icon']
                return [temp, feels_temp, weather_desc, icon_code]
            else:
                st.error("City not found or API key error")
    
       
def display_data():
    request = Request_weather(city,country)
    result = request.get_weather()
    st.write('## Result of the search')
    st.write(f'Location: {city}, {country.upper()}')
    st.write(f'The current temperature is {result[0]}°C, but it feels like {result[1]}°C')
    icon_url = f"https://openweathermap.org/img/wn/{result[3]}@2x.png"
    st.write(f'Weather description:')
    st.image(icon_url, caption=result[2].capitalize())
    
        
def main():
    global city, country
    
    st.header("Weather application", divider=True)
    st.markdown("## Get the weather condition anywhere you desire")
    
    col = st.columns(2)
    city = col[0].text_input('Name of the city you want to look up: ')
    country = col[1].text_input('Corresponding two-digit country code: ')
    st.write(f'You can find the official country code following the ISO 3166 at: https://www.iso.org/obp/ui/#search')
    
    if st.button('Search'):
        display_data()
    

if __name__ == '__main__':
    main()
