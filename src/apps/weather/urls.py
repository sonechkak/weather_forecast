from django.urls import path, include

from .views import (
    WeatherHomeView,
    WeatherHistoryView,
    AboutAPIView,
    AboutSiteView
)

app_name = 'weather'


urlpatterns = [
    path('', WeatherHomeView.as_view(), name='home'),
    path('history/', WeatherHistoryView.as_view(), name='history'),
    path('about-api/', AboutAPIView.as_view(), name='about_api'),
    path("about/", AboutSiteView.as_view(), name='about_site'),

    # API endpoints
    path("api/v1/", include("apps.weather.api.api_urls"), name="weather_api"),
]
