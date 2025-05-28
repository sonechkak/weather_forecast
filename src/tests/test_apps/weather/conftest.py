import pytest
from django.test import RequestFactory, Client

from apps.weather.models import City, WeatherSearch
from apps.weather.services.history_service import HistoryService
from apps.weather.services.weather_service import WeatherService


@pytest.fixture
def client():
    """Фикстура для Django test client."""
    return Client()


@pytest.fixture
def request_factory():
    """Фикстура для RequestFactory."""
    return RequestFactory()


@pytest.fixture
def sample_city():
    """Фикстура для тестового города."""
    return City.objects.create(
        name="Тестовый город",
        latitude=55.7558,
        longitude=37.6176,
        country="Россия"
    )


@pytest.fixture
def sample_cities():
    """Create sample cities for testing."""
    cities = []
    for i in range(3):
        city = City.objects.create(
            name=f"Тест Город {i+1}",
            latitude=55.0 + i * 0.1,
            longitude=37.0 + i * 0.1,
            country="Россия"
        )
        cities.append(city)
    return cities


@pytest.fixture
def sample_searches(sample_cities):
    """Фикстура для создания тестовых поисков."""
    searches = []
    for i, city in enumerate(sample_cities):
        for j in range(i + 1):  # Разное количество поисков для разных городов
            search = WeatherSearch.objects.create(
                session_key=f"session_{j}",
                city=city,
                weather_data={
                    "temperature": 20 + i,
                    "condition": f"condition_{i}"
                }
            )
            searches.append(search)
    return searches


@pytest.fixture
def mock_geocoding_response():
    """Фикстура для мока ответа geocoding API."""
    return {
        "results": [
            {
                "name": "Тест Город",
                "latitude": 55.7558,
                "longitude": 37.6176,
                "country": "Россия",
                "admin1": "Тест область"
            }
        ]
    }


@pytest.fixture
def mock_weather_response():
    """Фикстура для мока ответа weather API."""
    return {
        "current": {
            "temperature_2m": -5.2,
            "relative_humidity_2m": 80,
            "wind_speed_10m": 12.5,
            "weather_code": 71,
            "time": "2024-12-01T10:00"
        },
        "daily": {
            "time": ["2024-12-01", "2024-12-02"],
            "temperature_2m_max": [-2, -1],
            "temperature_2m_min": [-8, -6],
            "weather_code": [71, 61]
        },
        "latitude": 55.7558,
        "longitude": 37.6176,
        "timezone": "Europe/Moscow"
    }


@pytest.fixture
def mock_geocoding_api_response():
    """Фикстура для мока ответа Geocoding API."""
    return {
        "results": [
            {
                "name": "Тест Город",
                "latitude": 55.7558,
                "longitude": 37.6176,
                "country": "Россия",
                "admin1": "Тест область",
                "population": 1000000
            },
            {
                "name": "Тест Город 2",
                "latitude": 56.0,
                "longitude": 38.0,
                "country": "Россия",
                "admin1": "Тест область 2",
                "population": 500000
            }
        ]
    }


@pytest.fixture
def weather_service():
    """Фикстура сервиса погоды."""
    return WeatherService()


@pytest.fixture
def history_service():
    """Фикстура сервиса истории."""
    return HistoryService()


@pytest.fixture
def sample_weather_data():
    """Фикстура для тестовых данных о погоде."""
    return {
        "current": {
            "temperature": -5.2,
            "humidity": 80,
            "wind_speed": 12.5,
            "description": "Легкий снег"
        },
        "daily_forecast": [
            {
                "date": "2024-12-01",
                "temp_max": -2,
                "temp_min": -8,
                "description": "Снег"
            }
        ]
    }

