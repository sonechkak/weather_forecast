import pytest
from unittest.mock import Mock, patch
from django.urls import reverse
from urllib.parse import quote

from apps.weather.views import WeatherHomeView
from apps.weather.forms import WeatherSearchForm


@pytest.mark.django_db
def test_home_page_get(client):
    """Тест GET запроса на главную страницу."""
    response = client.get(reverse('weather:home'))

    assert response.status_code == 200
    assert 'form' in response.context
    assert isinstance(response.context['form'], WeatherSearchForm)
    assert 'previous_cities' in response.context
    assert response.context['previous_cities'] == []


@pytest.mark.django_db
def test_home_page_with_previous_cities_cookie(client):
    """Тест главной страницы с сохраненными городами в cookies."""
    encoded_cities = quote('Тест,Город', safe='')
    client.cookies['previous_cities'] = encoded_cities

    response = client.get(reverse('weather:home'))

    assert response.status_code == 200
    assert len(response.context['previous_cities']) == 1


@pytest.mark.django_db
@patch('apps.weather.services.weather_service.WeatherService')
def test_weather_search_api_error(mock_weather_service, client):
    """Тест обработки ошибки API при поиске."""
    mock_weather_instance = mock_weather_service.return_value
    mock_weather_instance.search_weather_by_city.side_effect = ValueError("Город не найден")
    data = {'city': 'НесуществующийГород'}

    response = client.get(reverse('weather:home'), data)

    assert response.status_code == 200
    assert "Город 'НесуществующийГород' не найден." in response.context['error_message']
    assert response.context['searched_city'] == 'НесуществующийГород'


@pytest.mark.django_db
def test_weather_search_invalid_form(client):
    """Тест поиска с невалидными данными."""
    response = client.get(reverse('weather:home'), {'city': ''})

    assert response.status_code == 200
    assert 'Пожалуйста, введите корректное название города' in response.context['error_message']


@pytest.mark.django_db
def test_history_page_empty(client):
    """Тест страницы истории без данных."""
    response = client.get(reverse('weather:history'))

    assert response.status_code == 200
    assert 'user_history' in response.context
    assert 'popular_cities' in response.context
    assert response.context['user_history'] == []


@pytest.mark.django_db
def test_about_api_page(client):
    """Тест страницы о API."""
    response = client.get(reverse('weather:about_api'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_about_site_page(client):
    """Тест страницы о сайте."""
    response = client.get(reverse('weather:about_site'))
    assert response.status_code == 200


@pytest.mark.django_db
@patch('requests.get')
def test_autocomplete_view_success(mock_get, client):
    """Тест успешного автодополнения."""
    mock_response = Mock()
    mock_response.json.return_value = {
        "results": [
            {
                "name": "Тест",
                "latitude": 55.7558,
                "longitude": 37.6176,
                "country": "Россия"
            }
        ]
    }
    mock_response.raise_for_status.return_value = None
    mock_get.return_value = mock_response

    response = client.get('/api/v1/autocomplete/', {'q': 'Тес'})

    assert response.status_code == 200
    data = response.json()
    assert len(data['suggestions']) > 0


@pytest.mark.django_db
def test_autocomplete_view_short_query(client):
    """Тест автодополнения с коротким запросом."""
    response = client.get('/api/v1/autocomplete/', {'q': 'Т'})

    assert response.status_code == 200
    data = response.json()
    assert data['suggestions'] == []


@pytest.mark.django_db
@patch('apps.weather.services.history_service.HistoryService')
def test_weather_stats_api(mock_service, client):
    """Тест API статистики."""
    mock_instance = mock_service.return_value
    mock_instance.get_popular_cities.return_value = [
        {'city': 'Тест', 'search_count': 10}
    ]

    response = client.get('/api/v1/stats/')

    assert response.status_code == 200
    data = response.json()
    assert 'popular_cities' in data


@pytest.mark.django_db
@patch('apps.weather.services.history_service.HistoryService')
@pytest.mark.django_db
def test_user_history_api_with_session(mock_service, client):
    """Тест API истории с сессией."""
    session = client.session
    session.save()

    mock_instance = mock_service.return_value
    mock_instance.get_history.return_value = [
        {'city': 'Тест', 'weather_data': {'temperature': 20}}
    ]

    response = client.get('/api/v1/user-history/')

    assert response.status_code == 200
    data = response.json()
    assert data['status'] == 'success'


@pytest.mark.django_db
def test_get_previous_cities_from_cookies(request_factory):
    """Тест извлечения предыдущих городов из cookies."""
    request = request_factory.get('/')
    encoded_cities = quote('Тест,Город', safe='')
    request.COOKIES = {'previous_cities': encoded_cities}

    view = WeatherHomeView()
    view.request = request

    cities = view._get_previous_cities()

    assert len(cities) == 1
    assert 'Тест,Город' in cities


@pytest.mark.django_db
def test_get_previous_cities_empty_cookies(request_factory):
    """Тест с пустыми cookies."""
    request = request_factory.get('/')
    request.COOKIES = {}

    view = WeatherHomeView()
    view.request = request

    cities = view._get_previous_cities()

    assert cities == []


@pytest.mark.django_db
def test_update_previous_cities(request_factory):
    """Тест обновления списка предыдущих городов."""
    request = request_factory.get('/')
    encoded_cities = quote('Город1,Город2', safe='')
    request.COOKIES = {'previous_cities': encoded_cities}

    view = WeatherHomeView()
    view.request = request

    view._update_previous_cities('НовыйГород')

    assert view.previous_cities[0] == 'НовыйГород'
    assert 'Город1,Город2' in view.previous_cities
    assert len(view.previous_cities) <= 5
