from django.contrib import admin

from .models import Season


@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('type', 'subtype', 'year', 'start_date', 'end_date', 'is_active')
    list_filter = ('type', 'subtype', 'is_active')
    search_fields = ('type', 'subtype', 'year')
