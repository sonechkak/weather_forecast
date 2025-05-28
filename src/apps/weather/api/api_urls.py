from django.urls import path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

from .api_views import (
    WeatherStatsAPIView,
    UserHistoryAPIView,
    APIRootView
)
from ..views import AutocompleteView

app_name = "weather_api"


urlpatterns = [
    path("stats/", WeatherStatsAPIView.as_view(), name="weather_stats"),
    path("user-history/", UserHistoryAPIView.as_view(), name="user_history"),
    path("root/", APIRootView.as_view(), name="api_root"),
    path("autocomplete/", AutocompleteView.as_view(), name="autocomplete"),

    # API документация
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('apredoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]
