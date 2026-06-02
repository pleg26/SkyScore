from django.contrib import admin

from .models import Airfield, Country


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('iso3', 'name')
    search_fields = ('iso3', 'name')


@admin.register(Airfield)
class AirfieldAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'country', 'lat', 'lon', 'alt')
    list_filter = ('country',)
    search_fields = ('code', 'name')
