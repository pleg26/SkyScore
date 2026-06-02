from django import forms

from .models import Airfield, Country


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['iso3', 'name']

    def clean_iso3(self):
        return self.cleaned_data['iso3'].strip().upper()


class AirfieldForm(forms.ModelForm):
    class Meta:
        model = Airfield
        fields = ['code', 'name', 'country', 'lat', 'lon', 'alt']
        labels = {
            'code': 'OACI Code',
            'name': 'Name',
            'country': 'Country',
            'lat': 'Latitude (decimal degrees)',
            'lon': 'Longitude (decimal degrees)',
            'alt': 'Altitude (feet)',
        }

    def clean_code(self):
        return self.cleaned_data['code'].strip().upper()
