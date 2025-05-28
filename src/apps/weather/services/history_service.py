from django.db.models import Count

from ..models import (
    WeatherSearch,
    City
)


class HistoryService:
    """Класс для работы с историей погоды."""

    def save_history(self, session_key: str, city: str, weather_data: dict) -> None:
        """Сохраняет историю поиска погоды."""

        city_obj, created = City.objects.get_or_create(name=city)
        WeatherSearch.objects.create(
            session_key=session_key,
            city=city_obj,
            weather_data=weather_data
        )

    def get_history(self, session_key: str) -> list[dict]:
        """Получает историю поиска погоды по ключу сессии."""

        searches = WeatherSearch.objects.filter(session_key=session_key).order_by('-search_date')
        history = []
        for search in searches:
            history.append({
                'city': search.city.name,
                'country': search.city.country,
                'search_date': search.search_date,
                'weather_data': search.weather_data
            })
        return history

    def clear_history(self, session_key: str) -> None:
        """Очищает историю поиска погоды по ключу сессии."""
        WeatherSearch.objects.filter(session_key=session_key).delete()

    def delete_search(self, search_id: int) -> None:
        """Удаляет конкретный поиск по его ID."""
        try:
            search = WeatherSearch.objects.get(id=search_id)
            search.delete()
        except WeatherSearch.DoesNotExist:
            raise ValueError(f"Поиск с ID {search_id} не найден")

    def get_popular_cities(self, limit: int = 10) -> list[dict]:
        """Получает список популярных городов на основе истории поиска."""

        popular_cities = (
            WeatherSearch.objects.values('city__name', 'city__country')
            .annotate(search_count=Count('id'))
            .order_by('-search_count')[:limit]
        )
        return [{'city': item['city__name'], 'country': item['city__country'], 'search_count': item['search_count']} for item in popular_cities]
