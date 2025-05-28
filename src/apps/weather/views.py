import logging

import requests
from django.http import JsonResponse
from django.shortcuts import render
from django.views import View
from django.views.generic import TemplateView
from urllib.parse import quote, unquote

from .services.history_service import HistoryService
from .services.weather_service import WeatherService
from .forms import WeatherSearchForm


logger = logging.getLogger(__name__)


class WeatherHomeView(TemplateView):
    """Главная страница с поиском погоды."""
    template_name = "weather/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = WeatherSearchForm()
        context["previous_cities"] = self._get_previous_cities()
        return context

    def get(self, request, *args, **kwargs):
        if "clear" in request.GET:
            return self._clear_history()

        if "city" in request.GET:
            return self._handle_weather_search()

        return super().get(request, *args, **kwargs)

    def _handle_weather_search(self):
        """Обрабатывает поиск погоды."""
        form = WeatherSearchForm(self.request.GET)
        context = self.get_context_data()

        if form.is_valid():
            city_name = form.cleaned_data["city"]

            try:
                weather_service = WeatherService()
                weather_data = weather_service.search_weather_by_city(city_name)

                history_service = HistoryService()
                session_key = self._get_or_create_session_key()
                history_service.save_history(session_key, city_name, weather_data)

                self._update_previous_cities(city_name)

                context.update({
                    "status": "success",
                    "weather_data": weather_data,
                    "searched_city": city_name,
                    "form": form
                })

            except ValueError as e:
                context.update({
                    "status": "error",
                    "error_message": str(e),
                    "searched_city": city_name,
                    "form": form
                })
        else:
            context.update({
                "status": "error",
                "error_message": "Пожалуйста, введите корректное название города",
                "form": form
            })

        response = render(self.request, self.template_name, context)
        self._set_previous_cities_cookie(response)
        return response

    def _get_previous_cities(self):
        """Получает список предыдущих городов из cookies."""
        previous_cities = self.request.COOKIES.get("previous_cities", "")
        if previous_cities:
            return [unquote(city) for city in previous_cities.split(",")]
        return []

    def _update_previous_cities(self, city_name):
        """Обновляет список предыдущих городов."""
        previous_cities = self._get_previous_cities()

        if city_name in previous_cities:
            previous_cities.remove(city_name)

        previous_cities.insert(0, city_name)
        self.previous_cities = previous_cities[:5]

    def _set_previous_cities_cookie(self, response):
        """Устанавливает cookie с предыдущими городами."""
        if hasattr(self, "previous_cities"):
            cookie_value = ",".join([quote(city) for city in self.previous_cities])
            response.set_cookie(
                "previous_cities",
                cookie_value,
                max_age=30 * 24 * 60 * 60  # 30 дней
            )

    def _clear_history(self):
        """Очищает историю предыдущих городов."""
        context = self.get_context_data()
        context["previous_cities"] = []
        context["status"] = "cleared"

        response = render(self.request, self.template_name, context)
        response.set_cookie("previous_cities", "", max_age=0)
        return response

    def _get_or_create_session_key(self):
        """Получает или создает ключ сессии."""
        if not self.request.session.session_key:
            self.request.session.create()
        return self.request.session.session_key


class CityAutocompleteView(View):
    """API для автодополнения городов."""

    def get(self, request):
        query = request.GET.get("q", "").strip()

        if len(query) < 2:
            return JsonResponse({"suggestions": []})

        try:
            weather_service = WeatherService()

            import requests
            params = {
                "name": query,
                "count": 5,
                "language": "ru",
                "format": "json"
            }

            response = requests.get(weather_service.GEOCODING_API_URL, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            suggestions = []

            if data.get("results"):
                for result in data["results"]:
                    city_name = result.get("name", "")
                    country = result.get("country", "")
                    admin1 = result.get("admin1", "")

                    display_name = city_name
                    if admin1 and admin1 != city_name:
                        display_name += f", {admin1}"
                    if country:
                        display_name += f", {country}"

                    suggestions.append({
                        "value": city_name,
                        "label": display_name
                    })

            return JsonResponse({"suggestions": suggestions})

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class WeatherHistoryView(TemplateView):
    """Страница истории поиска."""
    template_name = "weather/history.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        history_service = HistoryService()
        session_key = self.request.session.session_key

        if session_key:
            context["user_history"] = history_service.get_history(session_key)
        else:
            context["user_history"] = []

        context["popular_cities"] = history_service.get_popular_cities(10)

        return context


class AutocompleteView(View):
    """API для автодополнения поиска городов."""

    def get(self, request):
        query = request.GET.get("q", "").strip()

        # Короткий запрос
        if len(query) < 2:
            return JsonResponse({
                'status': 'success',
                'suggestions': [],
                'message': 'Минимум 2 символа для поиска',
                'query': query,
                'total_found': 0
            })

        suggestions = []

        # Получаем локальные предложения
        try:
            local_suggestions = self.get_local_suggestions(query)
            suggestions.extend(local_suggestions)
        except Exception as e:
            logger.error(f"Error getting local suggestions: {e}")

        # Получаем предложения из API
        try:
            api_suggestions = self.get_api_suggestions(query)
            suggestions.extend(api_suggestions)
        except Exception as e:
            logger.error(f"Error getting API suggestions: {e}")
            # Не прерываем выполнение, продолжаем с локальными результатами

        # Убираем дубликаты
        unique_suggestions = []
        seen_values = set()
        for suggestion in suggestions:
            if suggestion['value'] not in seen_values:
                unique_suggestions.append(suggestion)
                seen_values.add(suggestion['value'])

        # Ограничиваем результаты
        unique_suggestions = unique_suggestions[:10]

        return JsonResponse({
            'status': 'success',
            'suggestions': unique_suggestions,
            'query': query,
            'total_found': len(unique_suggestions)
        })

    def get_local_suggestions(self, query):
        """Получение предложений из локальной базы данных."""
        cities = City.objects.filter(name__icontains=query)[:5]

        suggestions = []
        for city in cities:
            suggestions.append({
                'value': city.name,
                'label': f"{city.name}, {city.country}",
                'source': 'local',
                'latitude': float(city.latitude) if city.latitude else None,
                'longitude': float(city.longitude) if city.longitude else None,
                'country': city.country
            })

        return suggestions

    def get_api_suggestions(self, query):
        """Получение предложений из внешнего API."""
        weather_service = WeatherService()

        params = {
            "name": query,
            "count": 5,
            "language": "ru",
            "format": "json"
        }

        try:
            response = requests.get(weather_service.GEOCODING_API_URL, params=params, timeout=5)
            response.raise_for_status()

            data = response.json()
            suggestions = []

            if data.get("results"):
                for result in data["results"]:
                    city_name = result.get("name", "")
                    country = result.get("country", "")
                    admin1 = result.get("admin1", "")

                    # Формируем название
                    display_name = city_name
                    if admin1 and admin1 != city_name:
                        display_name += f", {admin1}"
                    if country:
                        display_name += f", {country}"

                    suggestions.append({
                        "value": city_name,
                        "label": display_name,
                        "source": "api",
                        "latitude": result.get("latitude"),
                        "longitude": result.get("longitude"),
                        "country": country,
                        "admin1": admin1,
                        "population": result.get("population")
                    })

            return suggestions

        except requests.RequestException as e:
            return []
        except Exception as e:
            return []


class AboutAPIView(View):
    """API для получения информации о сервисе."""

    def get(self, request):
        return render(request, "weather/about_api.html", context={
            "title": "API документация",
        })


class AboutSiteView(View):
    """Страница с информацией о сайте."""

    def get(self, request):
        return render(request, "weather/about.html", {
            "title": "О сайте",
            "description": "Этот сайт предоставляет информацию о погоде в различных городах."
        })
