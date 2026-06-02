from django.contrib import admin

from .models import Competition, Competitor, Deck, NFZ, Task


@admin.register(Competitor)
class CompetitorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'country')
    list_filter = ('country',)
    search_fields = ('first_name', 'last_name')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(NFZ)
class NFZAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    search_fields = ('name',)


@admin.register(Competition)
class CompetitionAdmin(admin.ModelAdmin):
    list_display = ('name', 'level', 'sub_level', 'type', 'subtype', 'start_date', 'end_date', 'country', 'airfield', 'season')
    list_filter = ('level', 'sub_level', 'type', 'subtype', 'country', 'start_date')
    search_fields = ('name',)
    filter_horizontal = ('competitors', 'tasks', 'nfzs', 'decks')
