from django import forms


class WeatherSearchForm(forms.Form):
    """Форма для поиска погоды по городу."""

    city = forms.CharField(
        label="Город",
        max_length=100,
        widget=forms.TextInput(attrs={'placeholder': 'Введите название города'}),
    )

    def clean_city(self):
        """Проверяет корректность введенного названия города."""
        city = self.cleaned_data.get('city')
        if not city:
            raise forms.ValidationError("Это поле обязательно для заполнения.")
        return city
