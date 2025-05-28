import pytest
from unittest.mock import Mock, patch
from django.urls import reverse

from apps.weather.models import City, WeatherSearch
from test_apps.weather.conftest import mock_geocoding_api_response


@pytest.mark.django_db
def test_get_stats_success(api_client, sample_searches):
    """Тест успешного получения статистики."""
    response = api_client.get('/api/v1/stats/')

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert 'popular_cities' in data
    assert 'total_count' in data
    assert isinstance(data['popular_cities'], list)


@pytest.mark.django_db
def test_get_stats_ordering(api_client, sample_searches):
    """Тест сортировки городов по популярности."""
    response = api_client.get('/api/v1/stats/')

    assert response.status_code == 200
    data = response.json()
    popular_cities = data['popular_cities']

    if len(popular_cities) > 1:
        for i in range(len(popular_cities) - 1):
            assert popular_cities[i]['search_count'] >= popular_cities[i + 1]['search_count']


@pytest.mark.django_db
def test_get_history_no_session(api_client):
    """Тест получения истории без сессии."""
    response = api_client.get('/api/v1/user-history/')

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert data['history'] == []


@pytest.mark.django_db
def test_get_history_with_session(api_client, sample_searches):
    """Тест получения истории с сессией."""
    session = api_client.session
    session.save()

    city = City.objects.create(name="Тест Сессия", latitude=55.0, longitude=37.0, country="Россия")
    WeatherSearch.objects.create(
        session_key=session.session_key,
        city=city,
        weather_data={"temperature": 25}
    )

    response = api_client.get('/api/v1/user-history/')

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert len(data['history']) >= 1
    assert 'total_count' in data


@pytest.mark.django_db
def test_get_history_multiple_sessions(api_client, sample_cities):
    """Тест, что возвращается только история текущей сессии."""
    WeatherSearch.objects.create(
        session_key="other_session",
        city=sample_cities[0],
        weather_data={"temperature": 20}
    )

    session = api_client.session
    session.save()

    WeatherSearch.objects.create(
        session_key=session.session_key,
        city=sample_cities[1],
        weather_data={"temperature": 25}
    )

    response = api_client.get('/api/v1/user-history/')

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'
    assert len(data['history']) == 1
    assert data['history'][0]['city'] == "Тест Город 2"


@pytest.mark.django_db
def test_autocomplete_empty_query(api_client):
    """Тест автодополнения с пустым запросом."""
    response = api_client.get('/api/v1/autocomplete/')

    assert response.status_code == 200
    data = response.json()
    assert data['suggestions'] == []


@pytest.mark.django_db
def test_autocomplete_local_cities(api_client, sample_cities):
    """Тест автодополнения с локальными городами."""
    response = api_client.get('/api/v1/autocomplete/', {'q': 'Тест'})

    assert response.status_code == 200
    data = response.json()
    assert len(data['suggestions']) >= 1

    suggestion = data['suggestions'][0]
    assert 'value' in suggestion
    assert 'label' in suggestion
    assert 'source' in suggestion


@pytest.mark.django_db
@patch('requests.get')
def test_autocomplete_api_error(mock_get, api_client):
    """Тест обработки ошибки API."""
    mock_get.side_effect = Exception("API Error")

    response = api_client.get('/api/v1/autocomplete/', {'q': 'Тест'})

    assert response.status_code == 200


@pytest.mark.django_db
def test_autocomplete_limit_results(api_client):
    """Тест ограничения количества результатов."""
    for i in range(15):
        City.objects.create(
            name=f"Тест Город {i}",
            latitude=55.0 + i * 0.1,
            longitude=37.0 + i * 0.1,
            country="Россия"
        )

        response = api_client.get('/api/v1/autocomplete/', {'q': 'Тест'})

        assert response.status_code == 200
        data = response.json()
        assert len(data['suggestions']) <= 10


@pytest.mark.django_db
def test_autocomplete_response_format(api_client, sample_cities):
    """Тест формата ответа автодополнения."""
    response = api_client.get('/api/v1/autocomplete/', {'q': 'Тест'})

    assert response.status_code == 200
    data = response.json()

    assert 'status' in data
    assert 'suggestions' in data
    assert 'query' in data
    assert 'total_found' in data

    if data['suggestions']:
        suggestion = data['suggestions'][0]
        required_fields = ['value', 'label', 'source']
        for field in required_fields:
            assert field in suggestion
