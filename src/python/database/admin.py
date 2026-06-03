from django.contrib import admin
from django.contrib.auth import get_user_model

from .forms import CompetitorForm
from .models import Airfield, CartModel, Competitor, Country, EngineModel, Manufacturer, ULMModel, WingModel


User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'first_name', 'last_name', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    form = CompetitorForm
    list_display = ('first_name', 'last_name', 'aircraft_type', 'competitor_type', 'crew', 'user', 'country')
    list_filter = ('aircraft_type', 'competitor_type', 'country')
    search_fields = ('first_name', 'last_name', 'user__email')


@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(WingModel)
class WingModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer')
    list_filter = ('manufacturer',)
    search_fields = ('name', 'manufacturer__name')


@admin.register(CartModel)
class CartModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer')
    list_filter = ('manufacturer',)
    search_fields = ('name', 'manufacturer__name')


@admin.register(ULMModel)
class ULMModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer')
    list_filter = ('manufacturer',)
    search_fields = ('name', 'manufacturer__name')


@admin.register(EngineModel)
class EngineModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'manufacturer')
    list_filter = ('manufacturer',)
    search_fields = ('name', 'manufacturer__name')


@admin.register(Country)
class CountryAdmin(admin.ModelAdmin):
    list_display = ('iso3', 'name')
    search_fields = ('iso3', 'name')


@admin.register(Airfield)
class AirfieldAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'country', 'lat', 'lon', 'alt')
    list_filter = ('country',)
    search_fields = ('code', 'name')
