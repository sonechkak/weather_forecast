from django.http import JsonResponse
from rest_framework import permissions
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.weather.services.history_service import HistoryService


class WeatherStatsAPIView(APIView):
    """API для статистики поиска."""

    permission_classes = (AllowAny,)

    @extend_schema(
        summary="Статистика популярных городов",
        description="Возвращает список самых популярных городов по количеству поисковых запросов",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "success"},
                    "popular_cities": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "example": "Москва"},
                                "search_count": {"type": "integer", "example": 15},
                                "country": {"type": "string", "example": "Россия"}
                            }
                        }
                    },
                    "total_count": {"type": "integer", "example": 28}
                }
            }
        }
    )
    def get(self, request):
        try:
            history_service = HistoryService()
            popular_cities = history_service.get_popular_cities(20)

            return JsonResponse({
                "status": "success",
                "popular_cities": popular_cities,
                "total_count": len(popular_cities)
            })
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Ошибка получения статистики: {str(e)}"
            }, status=500)


class UserHistoryAPIView(APIView):
    """API для истории пользователя."""

    permission_classes = (AllowAny,)

    @extend_schema(
        summary="История поиска пользователя",
        description="Возвращает историю поиска текущего пользователя (по сессии)",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string", "example": "success"},
                    "history": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "city": {"type": "string", "example": "Москва"},
                                "weather_data": {"type": "object"},
                                "search_date": {"type": "string", "format": "date-time"}
                            }
                        }
                    },
                    "total_count": {"type": "integer", "example": 5}
                }
            }
        }
    )
    def get(self, request):
        session_key = request.session.session_key

        if not session_key:
            return JsonResponse({
                "status": "success",
                "history": [],
                "message": "Сессия не найдена"
            })

        try:
            history_service = HistoryService()
            user_history = history_service.get_history(session_key)

            return JsonResponse({
                "status": "success",
                "history": user_history,
                "total_count": len(user_history)
            })
        except Exception as e:
            return JsonResponse({
                "status": "error",
                "message": f"Ошибка получения истории: {str(e)}"
            }, status=500)


class APIRootView(APIView):
    """Корневой endpoint API с информацией о доступных методах."""

    permission_classes = (AllowAny,)

    @extend_schema(
        summary="API Root",
        description="Получение информации о доступных API endpoints",
        responses={
            200: {
                "type": "object",
                "properties": {
                    "status": {"type": "string"},
                    "message": {"type": "string"},
                    "version": {"type": "string"},
                    "endpoints": {"type": "object"}
                }
            }
        }
    )
    def get(self, request):
        return JsonResponse({
            "status": "success",
            "message": "Weather Service API",
            "version": "1.0.0",
            "description": "Наш сервис для получения информации о погоде по городам",
            "endpoints": {
                "autocomplete": {
                    "url": "/api/v1/autocomplete/",
                    "method": "GET",
                    "description": "Автодополнение названий городов",
                    "parameters": {"q": "поисковый запрос (минимум 2 символа)"}
                },
                "stats": {
                    "url": "/api/v1/stats/",
                    "method": "GET",
                    "description": "Статистика популярных городов"
                },
                "user_history": {
                    "url": "/api/v1/user-history/",
                    "method": "GET",
                    "description": "История поиска пользователя"
                }
            },
            "data_source": "Open-Meteo API",
            "documentation": request.build_absolute_uri('/about-api/')
        })
