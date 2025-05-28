import requests
from decouple import config

from ..enums.weather_codes import weather_codes
from ..models import City


class WeatherService:
    """Сервис для получения данных о погоде через Open-Meteo API."""

    GEOCODING_API_URL = config("GEOCODING_API_URL", default="https://geocoding-api.open-meteo.com/v1/search")
    WEATHER_API_URL = config("WEATHER_API_BASE_URL", default="https://api.open-meteo.com/v1/forecast")

    def get_city_coordinates(self, city_name: str) -> tuple[float, float]:
        """Получает координаты города по его названию."""
        try:
            city = City.objects.get(name__iexact=city_name)
            return city.latitude, city.longitude
        except City.DoesNotExist:
            return self._fetch_coordinates_from_api(city_name)

    def get_weather_forecast(self, latitude: float, longitude: float) -> dict:
        """Получает прогноз погоды по координатам через Open-Meteo."""
        try:
            params = {
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,weather_code,wind_speed_10m,relative_humidity_2m",
                "daily": "temperature_2m_max,temperature_2m_min,weather_code",
                "timezone": "auto",
                "forecast_days": 7
            }

            response = requests.get(self.WEATHER_API_URL, params=params, timeout=10)
            response.raise_for_status()

            return response.json()

        except requests.RequestException as e:
            raise ValueError(f"Ошибка при получении данных о погоде: {str(e)}")

    def format_weather_data(self, weather_data: dict) -> dict:
        """Форматирует данные о погоде для отображения."""
        current = weather_data.get("current", {})
        daily = weather_data.get("daily", {})

        # Текущая погода
        current_weather = {
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "wind_speed": current.get("wind_speed_10m"),
            "weather_code": current.get("weather_code"),
            "description": self._get_weather_description(current.get("weather_code", 0)),
        }

        # Прогноз на неделю
        daily_forecast = []
        if daily.get("time"):
            for i in range(len(daily["time"])):
                daily_forecast.append({
                    "date": daily["time"][i],
                    "temp_max": daily.get("temperature_2m_max", [])[i] if i < len(
                        daily.get("temperature_2m_max", [])) else None,
                    "temp_min": daily.get("temperature_2m_min", [])[i] if i < len(
                        daily.get("temperature_2m_min", [])) else None,
                    "weather_code": daily.get("weather_code", [])[i] if i < len(
                        daily.get("weather_code", [])) else None,
                    "description": self._get_weather_description(
                        daily.get("weather_code", [])[i] if i < len(daily.get("weather_code", [])) else 0),
                })

        return {
            "current": current_weather,
            "daily_forecast": daily_forecast
        }

    def _fetch_coordinates_from_api(self, city_name: str) -> tuple[float, float]:
        """Получает координаты города через Open-Meteo Geocoding API."""
        try:
            params = {
                "name": city_name,
                "count": 1,
                "language": "ru",
                "format": "json"
            }

            response = requests.get(self.GEOCODING_API_URL, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()

            if not data.get("results"):
                raise ValueError(f"Город '{city_name}' не найден.")

            result = data["results"][0]
            latitude = result["latitude"]
            longitude = result["longitude"]
            country = result.get("country", "")
            api_city_name = result.get("name", city_name)

            city, created = City.objects.get_or_create(
                name__iexact=api_city_name,
                defaults={
                    "name": api_city_name,
                    "latitude": latitude,
                    "longitude": longitude,
                    "country": country
                }
            )

            return latitude, longitude

        except requests.RequestException as e:
            raise ValueError(f"Ошибка при получении координат города: {str(e)}")

    def _get_weather_description(self, weather_code: int) -> str:
        """Получает текстовое описание погоды по коду погоды."""
        weather_descriptions = weather_codes
        return weather_descriptions.get(weather_code, "Неизвестно")

    def search_weather_by_city(self, city_name: str) -> dict:
        """Полный поиск погоды по названию города."""
        try:
            latitude, longitude = self.get_city_coordinates(city_name)
            raw_weather_data = self.get_weather_forecast(latitude, longitude)

            formatted_data = self.format_weather_data(raw_weather_data)
            return formatted_data

        except ValueError:
            raise
        except Exception as e:
            raise ValueError(f"Неожиданная ошибка: {str(e)}")
