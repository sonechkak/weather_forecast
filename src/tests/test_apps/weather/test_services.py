import pytest
from unittest.mock import Mock, patch
import requests

from apps.weather.models import City, WeatherSearch


@pytest.mark.django_db
@patch('apps.weather.services.weather_service.requests.get')
def test_get_city_coordinates_from_api(mock_get, client, weather_service, mock_geocoding_response):
    """Тест получения координат города через API."""
    mock_response = Mock()
    mock_response.json.return_value = mock_geocoding_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    lat, lon = weather_service.get_city_coordinates("Новый Город")

    assert lat == 55.7558
    assert lon == 37.6176
    mock_get.assert_called_once()

    city = City.objects.get(name="Тест Город")
    assert city.latitude == 55.7558
    assert city.longitude == 37.6176


@pytest.mark.django_db
@patch('apps.weather.services.weather_service.requests.get')
def test_get_city_coordinates_api_not_found(mock_get, client, weather_service):
    """Тест обработки случая когда город не найден в API."""
    mock_response = Mock()
    mock_response.json.return_value = {"results": []}
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    with pytest.raises(ValueError, match="Город 'НесуществующийГород' не найден"):
        weather_service.get_city_coordinates("НесуществующийГород")


@pytest.mark.django_db
@patch('apps.weather.services.weather_service.requests.get')
def test_get_city_coordinates_api_error(mock_get, client, weather_service):
    """Тест обработки ошибки API."""
    mock_get.side_effect = requests.RequestException("API недоступен")

    with pytest.raises(ValueError, match="Ошибка при получении координат города"):
        weather_service.get_city_coordinates("Тест")


@pytest.mark.django_db
@patch('apps.weather.services.weather_service.requests.get')
def test_get_weather_forecast(mock_get, client, weather_service, mock_weather_response):
    """Тест получения прогноза погоды."""
    mock_response = Mock()
    mock_response.json.return_value = mock_weather_response
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    result = weather_service.get_weather_forecast(55.7558, 37.6176)

    assert result == mock_weather_response
    mock_get.assert_called_once()


@pytest.mark.django_db
@patch('apps.weather.services.weather_service.requests.get')
def test_get_weather_forecast_api_error(mock_get, client, weather_service):
    """Тест обработки ошибки при получении прогноза."""
    mock_get.side_effect = requests.RequestException("Weather API недоступен")

    with pytest.raises(ValueError, match="Ошибка при получении данных о погоде"):
        weather_service.get_weather_forecast(55.7558, 37.6176)


@pytest.mark.django_db
def test_format_weather_data(client, weather_service, mock_weather_response):
    """Тест форматирования данных о погоде."""
    result = weather_service.format_weather_data(mock_weather_response)

    assert 'current' in result
    assert 'daily_forecast' in result

    current = result['current']
    assert current['temperature'] == -5.2
    assert current['humidity'] == 80
    assert current['wind_speed'] == 12.5
    assert current['description'] == "Легкий снег"

    daily = result['daily_forecast']
    assert len(daily) == 2
    assert daily[0]['temp_max'] == -2
    assert daily[0]['temp_min'] == -8


@pytest.mark.django_db
def test_get_weather_description(client, weather_service):
    """Тест получения описания погоды по коду."""
    assert weather_service._get_weather_description(0) == "Ясно"
    assert weather_service._get_weather_description(71) == "Легкий снег"
    assert weather_service._get_weather_description(999) == "Неизвестно"


@pytest.mark.django_db
def test_get_history(client, history_service, sample_city):
    """Тест получения истории поиска."""
    WeatherSearch.objects.create(
        session_key="test_session",
        city=sample_city,
        weather_data={"temp": 20}
    )

    WeatherSearch.objects.create(
        session_key="test_session",
        city=sample_city,
        weather_data={"temp": 25}
    )

    WeatherSearch.objects.create(
        session_key="other_session",
        city=sample_city,
        weather_data={"temp": 30}
    )

    history = history_service.get_history("test_session")

    assert len(history) == 2