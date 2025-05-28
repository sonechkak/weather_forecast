import pytest
from django.db import IntegrityError
from django.core.exceptions import ValidationError
from django.utils import timezone

from apps.weather.models import City, WeatherSearch


@pytest.mark.django_db
def test_city_creation():
    """Тест создания города."""
    city = City.objects.create(
        name="Санкт-Петербург",
        latitude=59.9311,
        longitude=30.3609,
        country="Россия"
    )

    assert city.name == "Санкт-Петербург"
    assert city.latitude == 59.9311
    assert city.longitude == 30.3609
    assert city.country == "Россия"
    assert str(city) == "Санкт-Петербург, Россия"


@pytest.mark.django_db
def test_city_unique_name_constraint():
    """Тест уникальности названия города."""
    City.objects.create(
        name="Уникальный город",
        latitude=55.0,
        longitude=37.0,
        country="Россия"
    )

    with pytest.raises(IntegrityError):
        City.objects.create(
            name="Уникальный город",
            latitude=56.0,
            longitude=38.0,
            country="Россия"
        )


@pytest.mark.django_db
def test_city_str_method(sample_city):
    """Тест строкового представления города."""
    assert str(sample_city) == "Тестовый город, Россия"


@pytest.mark.django_db
def test_city_coordinates_validation():
    """Тест валидации координат."""
    city = City(
        name="Тест валидный",
        latitude=45.0,
        longitude=90.0,
        country="Тест"
    )
    city.full_clean()


@pytest.mark.django_db
def test_city_without_country():
    """Тест создания города без страны."""
    city = City.objects.create(
        name="Неизвестный город",
        latitude=0.0,
        longitude=0.0,
        country=""
    )
    assert city.country == ""
    assert str(city) == "Неизвестный город, "


@pytest.mark.django_db
def test_weather_search_creation(sample_city, sample_weather_data):
    """Тест создания записи поиска погоды."""
    search = WeatherSearch.objects.create(
        session_key="test_session_123",
        city=sample_city,
        weather_data=sample_weather_data
    )

    assert search.session_key == "test_session_123"
    assert search.city == sample_city
    assert search.weather_data == sample_weather_data
    assert search.search_date is not None


@pytest.mark.django_db
def test_weather_search_auto_date(sample_city, sample_weather_data):
    """Тест автоматического установления даты поиска."""
    before_creation = timezone.now()

    search = WeatherSearch.objects.create(
        session_key="test_session",
        city=sample_city,
        weather_data=sample_weather_data
    )

    after_creation = timezone.now()

    assert before_creation <= search.search_date <= after_creation


@pytest.mark.django_db
def test_weather_search_json_field(sample_city):
    """Тест JSON поля для данных о погоде."""
    weather_data = {
        "temperature": 25.5,
        "condition": "sunny",
        "nested": {
            "humidity": 65,
            "pressure": 1013
        }
    }

    search = WeatherSearch.objects.create(
        session_key="json_test",
        city=sample_city,
        weather_data=weather_data
    )

    search.refresh_from_db()

    assert search.weather_data["temperature"] == 25.5
    assert search.weather_data["condition"] == "sunny"
    assert search.weather_data["nested"]["humidity"] == 65


@pytest.mark.django_db
def test_weather_search_cascade_delete(sample_weather_data):
    """Тест каскадного удаления при удалении города."""
    city = City.objects.create(
        name="Город для удаления",
        latitude=55.0,
        longitude=37.0,
        country="Тест"
    )

    search = WeatherSearch.objects.create(
        session_key="cascade_test",
        city=city,
        weather_data=sample_weather_data
    )

    city_id = city.id
    search_id = search.id

    city.delete()

    assert not City.objects.filter(id=city_id).exists()
    assert not WeatherSearch.objects.filter(id=search_id).exists()


@pytest.mark.django_db
def test_weather_search_filter_by_session(sample_city, sample_weather_data):
    """Тест фильтрации поиска по сессии."""
    search1 = WeatherSearch.objects.create(
        session_key="session_a",
        city=sample_city,
        weather_data=sample_weather_data
    )

    search2 = WeatherSearch.objects.create(
        session_key="session_b",
        city=sample_city,
        weather_data=sample_weather_data
    )

    session_a_searches = WeatherSearch.objects.filter(session_key="session_a")
    session_b_searches = WeatherSearch.objects.filter(session_key="session_b")

    assert session_a_searches.count() == 1
    assert session_b_searches.count() == 1
    assert session_a_searches.first() == search1
    assert session_b_searches.first() == search2


@pytest.mark.django_db
def test_city_weather_searches_relationship(sample_weather_data):
    """Тест связи город-поиски."""
    city = City.objects.create(
        name="Город для связей",
        latitude=55.0,
        longitude=37.0,
        country="Тест"
    )

    search1 = WeatherSearch.objects.create(
        session_key="rel_test_1",
        city=city,
        weather_data=sample_weather_data
    )

    search2 = WeatherSearch.objects.create(
        session_key="rel_test_2",
        city=city,
        weather_data=sample_weather_data
    )

    city_searches = city.weathersearch_set.all()
    assert city_searches.count() == 2
    assert search1 in city_searches
    assert search2 in city_searches


@pytest.mark.django_db
def test_multiple_cities_searches(sample_weather_data):
    """Тест поисков для нескольких городов."""
    city1 = City.objects.create(
        name="Город1",
        latitude=55.0,
        longitude=37.0,
        country="Страна1"
    )

    city2 = City.objects.create(
        name="Город2",
        latitude=56.0,
        longitude=38.0,
        country="Страна2"
    )

    WeatherSearch.objects.create(
        session_key="multi_test",
        city=city1,
        weather_data=sample_weather_data
    )

    WeatherSearch.objects.create(
        session_key="multi_test",
        city=city2,
        weather_data=sample_weather_data
    )

    assert city1.weathersearch_set.count() == 1
    assert city2.weathersearch_set.count() == 1

    session_searches = WeatherSearch.objects.filter(session_key="multi_test")
    assert session_searches.count() == 2
