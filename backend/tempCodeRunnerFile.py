import requests
from config import OPENWEATHER_API_KEY

def get_weather(location: str) -> str:
    """
    Fetches current weather for a location using OpenWeatherMap API.
    Returns a user-friendly string or error message.
    """
    api_key = OPENWEATHER_API_KEY  # Use the imported config variable!
    if not api_key:
        return "Weather service is not configured (missing API key)."
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": location,
        "appid": api_key,
        "units": "metric",
    }
    try:
        resp = requests.get(url, params=params, timeout=8)
        data = resp.json()
        if resp.status_code != 200:
            # Show API error message for easier debugging
            return f"Could not get weather for '{location}': {data.get('message', 'Unknown error')}"
        weather = data["weather"][0]["description"]
        temp = round(data["main"]["temp"])
        city = data.get("name", location)
        return f"The weather in {city} is {weather} with {temp}°C."
    except Exception as e:
        return f"Error fetching weather: {e}"

if __name__ == "__main__":
    print("API KEY:", OPENWEATHER_API_KEY)
    print(get_weather("Napa"))
    print(get_weather("London"))
    print(get_weather("Delhi"))

