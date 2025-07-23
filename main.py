from dotenv import load_dotenv
import os
import requests

load_dotenv()  # Charge le contenu de .env dans l'environnement

api_key = os.getenv('api_key')

def get_weather(city_name, country_code, key):
   #r = requests.get('https://api.openweathermap.org/data/3.0/onecall?lat=51.5098&lon=-0.1180&units=metric&appid={key}')
    r = requests.get(f'http://api.openweathermap.org/geo/1.0/direct?q={city_name},{country_code}&appid={key}')
    print(r.status_code)
    print(r.json())
    
get_weather('Paris', 'fr', api_key)