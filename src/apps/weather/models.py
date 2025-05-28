from django.db import models


class City(models.Model):
    """Модель для хранения информации о городах."""

    name = models.CharField("Название", max_length=100, unique=True)
    country = models.CharField("Страна", max_length=100)
    latitude = models.FloatField("Широта")
    longitude = models.FloatField("Долгота")

    def __str__(self):
        return f"{self.name}, {self.country}"


class WeatherSearch(models.Model):
    """Модель для хранения информации о поиске погоды по городу."""

    session_key = models.CharField("Ключ сессии", max_length=255, db_index=True)
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    search_date = models.DateTimeField("Дата поиска", auto_now_add=True)
    weather_data = models.JSONField("Данные о погоде", blank=True, null=True)

    def __str__(self):
        return f"Поиск погоды для {self.city.name} ({self.search_date})"
