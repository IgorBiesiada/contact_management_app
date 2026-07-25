import requests
from django.core.cache import cache

def get_weather_for_city(city):
    """
    Retrieves current weather data for a specified city.
    
        This function uses a two-step API process:
        1. Geocodes the city name to latitude and longitude using Nominatim (OpenStreetMap).
        2. Fetches current weather conditions using the Open-Meteo API.
        To optimize performance and avoid rate limits, the result is cached 
        for 30 minutes (1800 seconds).
        Args:
            city (str): The name of the city to look up.
        Returns:
            dict: A dictionary containing 'temperature', 'humidity', 'wind_speed', 
                  'lat', and 'lon'.
            None: If the city parameter is empty or the city cannot be found.
    """

    if not city:
        return None

    cache_key = f'weather_{city}'
    weather_cache_data = cache.get(cache_key)

    if weather_cache_data:
        return weather_cache_data
        
    else:
        open_street_map = f'https://nominatim.openstreetmap.org/search?q={city}&format=json&limit=1'

        # we need headers for our open street map api otherwise, we'll get a 403 error
        headers = {
            'User-Agent': 'RekrutacjaApka'
        }

        response = requests.get(open_street_map, headers=headers)
        data = response.json()

        if not data:
            return None
        
        #longitude and latitude for second api
        lat = data[0]['lat']
        lon = data[0]['lon']

        open_meteo = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,wind_speed_10m'

        #in this api we dont need to make header
        response_weather = requests.get(open_meteo)
        weather_data = response_weather.json()

        # data from open meteo api
        temperature = weather_data['current']['temperature_2m']
        humidity = weather_data['current']['relative_humidity_2m']
        wind_speed = weather_data['current']['wind_speed_10m']        

        weather_cache_data = {
            'temperature': temperature,
            'humidity': humidity,
            'wind_speed': wind_speed,
            'lat': lat,
            'lon': lon
        }

        #cache result for 30 minutes
        cache.set(cache_key, weather_cache_data, timeout=1800)

        return weather_cache_data
