import requests
import os
from typing import Dict, Optional
from dotenv import load_dotenv


class WeatherSystem:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"

    def _get_weather_data(self, city: str) -> Optional[Dict]:
        """Get current weather data for a city"""
        try:
            url = f"{self.base_url}/weather"
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric",  # For Celsius
            }
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error getting weather data: {e}")
            return None

    def _get_forecast_data(self, city: str) -> Optional[Dict]:
        """Get 5-day forecast data for a city"""
        try:
            url = f"{self.base_url}/forecast"
            params = {"q": city, "appid": self.api_key, "units": "metric"}
            response = requests.get(url, params=params)
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Error getting forecast data: {e}")
            return None

    def _extract_city_name(self, command: str) -> str:
        """Extract city name from command"""
        command = command.lower()
        # Handle different command formats
        if "forecast" in command:
            city = command.split("forecast", 1)[1]
        elif "weather in" in command:
            city = command.split("weather in", 1)[1]
        elif "weather for" in command:
            city = command.split("weather for", 1)[1]
        else:
            city = command.split("weather", 1)[1]

        return city.strip()

    def _format_weather_response(self, data: Dict) -> str:
        """Format current weather data into readable text"""
        try:
            temp = data["main"]["temp"]
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            description = data["weather"][0]["description"]
            wind_speed = data["wind"]["speed"]
            city_name = data["name"]

            response = (
                f"Current weather in {city_name}: {description}. "
                f"Temperature is {temp:.1f}°C, feels like {feels_like:.1f}°C. "
                f"Humidity is {humidity}% with wind speed of {wind_speed} meters per second."
            )
            return response
        except KeyError:
            return "Sorry, I couldn't process the weather data."

    def _format_forecast_response(self, data: Dict) -> str:
        """Format forecast data into readable text"""
        try:
            city_name = data["city"]["name"]
            forecast_list = data["list"][:5]  # Get next 5 time slots

            response = [f"Weather forecast for {city_name}:"]
            for forecast in forecast_list:
                temp = forecast["main"]["temp"]
                description = forecast["weather"][0]["description"]
                date_time = forecast["dt_txt"].split()[1][:5]  # Get time only
                response.append(f"At {date_time}: {description}, {temp:.1f}°C")

            return "\n".join(response)
        except KeyError:
            return "Sorry, I couldn't process the forecast data."

    def process_weather_command(self, command: str) -> str:
        """Process weather command and return response"""
        try:
            city = self._extract_city_name(command)
            if not city:
                return "Please specify a city for the weather check."

            if "forecast" in command.lower():
                data = self._get_forecast_data(city)
                if data and "cod" in str(data.get("cod", "")):
                    return self._format_forecast_response(data)
            else:
                data = self._get_weather_data(city)
                if data and data.get("cod") == 200:
                    return self._format_weather_response(data)

            return f"Sorry, I couldn't get weather information for {city}."

        except Exception as e:
            print(f"Error processing weather command: {e}")
            return "Sorry, I encountered an error getting the weather information."
