from dotenv import load_dotenv
import os
import requests


load_dotenv()  # Load the content of .env into the environement 

class Request_weather():
    api_key = os.getenv('api_key')
    
    def __init__(self, city_name, country_code):
        self.city_name = city_name
        self.country_code = country_code
    
    def get_coordinate(self):
        try:
            r1 = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={self.city_name},{self.country_code}&appid={self.__class__.api_key}', timeout=2)
        except requests.exceptions.Timeout:
            print("Sorry, the server is taking too long")
        else:
            result = r1.json()
            lat = result[0]['lat']
            lon = result[0]['lon']
        return [lat, lon]
    
    def get_weather(self):
        necessary_data = self.get_coordinate()
        try:
            r2 = requests.get(f'https://api.openweathermap.org/data/3.0/onecall?lat={necessary_data[0]}&lon={necessary_data[1]}&exclude=hourly,daily&units=metric&appid={self.__class__.api_key}', timeout=2)
        except requests.exceptions.Timeout:
            print("Sorry, the server is taking too long")
        else: 
            data = r2.json()
            temp = data['current']['temp']
            feels_temp = data['current']['feels_like']
            weather_desc = data['current']['weather'][0]['description']
        return [temp, feels_temp, weather_desc]
    
    def __str__(self):
        weather = self.get_weather()
        return (f'Loaction: {self.city_name}, {self.country_code.upper()}\n'
        f'The current temperature is {weather[0]}°C but it feels like {weather[1]}°C\n'
        f'Weather description: {weather[2]}')
       


city = input('Enter the name of the city you want to look up: ')
country = input('Enter the corresponding country code: ')

request = Request_weather(city,country)
print(request)
        
