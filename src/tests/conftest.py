import os
import sys
import django
import pytest
import requests

from unittest.mock import patch
from django.conf import settings
from django.test import Client

src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
if src_path not in sys.path:
    sys.path.insert(0, src_path)

# Настройка Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.test')
django.setup()

# Импорты после настройки Django
from apps.weather.models import City, WeatherSearch


@pytest.fixture(scope='session')
def django_db_setup(django_db_setup, django_db_blocker):
    """Настройка тестовой базы данных."""
    with django_db_blocker.unblock():
        from django.core.management import call_command
        call_command('migrate', '--run-syncdb', verbosity=0)


@pytest.fixture
def api_client():
    """Фикстура для API клиента."""
    client = Client()
    # Инициализируем сессию
    client.session.create()
    return client


@pytest.fixture
def authenticated_client(django_user_model):
    """Фикстура для аутентифицированного клиента."""
    client = Client()

    user = django_user_model.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )

    client.force_login(user)
    return client, user


@pytest.fixture
def sample_session_key():
    """Фикстура для тестового ключа сессии."""
    return 'test_session_key_12345'


@pytest.fixture
def mock_requests():
    """Фикстура для мокирования requests."""
    with patch.object(requests, 'get') as mock_get:
        yield mock_get


@pytest.fixture
def sample_weather_data():
    """Фикстура с примером данных о погоде."""
    return {
        "current": {
            "temperature": 22.5,
            "humidity": 65,
            "wind_speed": 8.2,
            "weather_code": 1,
            "description": "В основном ясно"
        },
        "daily_forecast": [
            {
                "date": "2024-12-01",
                "temp_max": 25,
                "temp_min": 18,
                "weather_code": 1,
                "description": "В основном ясно"
            },
            {
                "date": "2024-12-02",
                "temp_max": 23,
                "temp_min": 16,
                "weather_code": 2,
                "description": "Переменная облачность"
            }
        ]
    }


@pytest.fixture
def sample_city_data():
    """Фикстура с данными города."""
    return {
        'name': 'Москва',
        'latitude': 55.7558,
        'longitude': 37.6176,
        'country': 'Россия'
    }


@pytest.fixture
def multiple_cities_data():
    """Фикстура с данными нескольких городов."""
    return [
        {
            'name': 'Москва',
            'latitude': 55.7558,
            'longitude': 37.6176,
            'country': 'Россия'
        },
        {
            'name': 'Санкт-Петербург',
            'latitude': 59.9311,
            'longitude': 30.3609,
            'country': 'Россия'
        },
        {
            'name': 'Новосибирск',
            'latitude': 55.0084,
            'longitude': 82.9357,
            'country': 'Россия'
        }
    ]


@pytest.fixture
def mock_open_meteo_geocoding():
    """Фикстура для мокирования Open-Meteo Geocoding API."""
    return {
        "results": [
            {
                "name": "Москва",
                "latitude": 55.7558,
                "longitude": 37.6176,
                "country": "Россия",
                "admin1": "Москва",
                "population": 12506000
            },
            {
                "name": "Московский",
                "latitude": 55.5962,
                "longitude": 37.3564,
                "country": "Россия",
                "admin1": "Московская область",
                "population": 72000
            }
        ]
    }


@pytest.fixture
def mock_geocoding_api_response():
    """Alias для совместимости с другими тестами."""
    return {
        "results": [
            {
                "name": "Новый Город",
                "latitude": 55.7558,
                "longitude": 37.6176,
                "country": "Russia",
                "admin1": "Moscow",
                "population": 1000000
            },
            {
                "name": "Новосибирск",
                "latitude": 55.0084,
                "longitude": 82.9357,
                "country": "Russia",
                "admin1": "Novosibirsk Oblast",
                "population": 1500000
            }
        ]
    }


@pytest.fixture
def mock_geocoding_response():
    """Mock response for geocoding service tests."""
    return {
        "results": [
            {
                "name": "Тест Город",
                "latitude": 55.7558,
                "longitude": 37.6176,
                "country": "Russia",
                "admin1": "Moscow"
            }
        ]
    }


@pytest.fixture
def mock_open_meteo_weather():
    """Фикстура для мокирования Open-Meteo Weather API."""
    return {
        "current": {
            "temperature_2m": 22.5,
            "relative_humidity_2m": 65,
            "wind_speed_10m": 8.2,
            "weather_code": 1,
            "time": "2024-12-01T12:00"
        },
        "daily": {
            "time": ["2024-12-01", "2024-12-02", "2024-12-03"],
            "temperature_2m_max": [25, 23, 21],
            "temperature_2m_min": [18, 16, 14],
            "weather_code": [1, 2, 3],
            "precipitation_sum": [0, 0.2, 1.5]
        },
        "latitude": 55.7558,
        "longitude": 37.6176,
        "timezone": "Europe/Moscow"
    }


@pytest.fixture
def mock_weather_response():
    """Alias для совместимости."""
    return {
        "current": {
            "time": "2024-12-01T12:00",
            "temperature_2m": -5.2,
            "relative_humidity_2m": 80,
            "wind_speed_10m": 12.5,
            "weather_code": 71
        },
        "daily": {
            "time": ["2024-12-01", "2024-12-02"],
            "temperature_2m_max": [-2, -1],
            "temperature_2m_min": [-8, -5],
            "weather_code": [71, 0]
        }
    }


@pytest.fixture
def create_test_cities(db):
    """Фикстура для создания тестовых городов в БД."""
    cities = []
    cities_data = [
        ("Москва", 55.7558, 37.6176, "Россия"),
        ("Санкт-Петербург", 59.9311, 30.3609, "Россия"),
        ("Новосибирск", 55.0084, 82.9357, "Россия"),
    ]

    for name, lat, lon, country in cities_data:
        city = City.objects.create(
            name=name,
            latitude=lat,
            longitude=lon,
            country=country
        )
        cities.append(city)

    return cities


@pytest.fixture
def sample_cities(db):
    """Фикстура для создания образцов городов."""
    cities = []
    for i in range(3):
        city = City.objects.create(
            name=f"Тест Город {i + 1}",
            latitude=55.0 + i * 0.1,
            longitude=37.0 + i * 0.1,
            country="Россия"
        )
        cities.append(city)
    return cities


@pytest.fixture
def sample_city(db):
    """Фикстура для создания одного города."""
    return City.objects.create(
        name="Тестовый город",
        latitude=55.7558,
        longitude=37.6176,
        country="Россия"
    )


@pytest.fixture
def create_test_searches(create_test_cities, sample_session_key, db):
    """Фикстура для создания тестовых поисков."""
    searches = []
    weather_data = {
        "temperature": 20,
        "condition": "sunny"
    }

    for city in create_test_cities[:2]:
        search = WeatherSearch.objects.create(
            session_key=sample_session_key,
            city=city,
            weather_data=weather_data
        )
        searches.append(search)

    return searches


@pytest.fixture
def sample_searches(sample_cities, db):
    """Фикстура для создания образцов поисков."""
    searches = []
    session_keys = ['session1', 'session2', 'session3']

    for i, city in enumerate(sample_cities):
        for j, session_key in enumerate(session_keys):
            for k in range(j + 1):
                search = WeatherSearch.objects.create(
                    session_key=session_key,
                    city=city,
                    weather_data={
                        "temperature": 20 + i + k,
                        "humidity": 60 + i * 5,
                        "description": f"Test weather {i}-{j}-{k}"
                    }
                )
                searches.append(search)
    return searches


@pytest.fixture
def weather_service(db):
    """Weather service instance for tests."""
    from apps.weather.services.weather_service import WeatherService
    return WeatherService()


@pytest.fixture
def history_service(db):
    """History service instance for tests."""
    from apps.weather.services.history_service import HistoryService
    return HistoryService()


@pytest.fixture(autouse=True)
def setup_test_environment_fixture(settings):
    """Настройка тестового окружения."""
    settings.CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

    settings.PASSWORD_HASHERS = [
        'django.contrib.auth.hashers.MD5PasswordHasher',
    ]

    for db_config in settings.DATABASES.values():
        if 'ATOMIC_REQUESTS' not in db_config:
            db_config['ATOMIC_REQUESTS'] = True