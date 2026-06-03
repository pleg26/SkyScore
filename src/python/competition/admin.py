from django.contrib import admin
from django import forms
from django.db.models import Q

from database.models import Competitor

from .models import Competition, Deck, NFZ, Task


class CompetitionAdminForm(forms.ModelForm):
    class Meta:
        model = Competition
        fields = '__all__'
        labels = {
            'type': 'Aircraft type',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        selected_aircraft_type = None
        if self.is_bound:
            selected_aircraft_type = (self.data.get('type') or '').strip().upper()
        elif self.instance and self.instance.pk:
            selected_aircraft_type = self.instance.type

        eligible_queryset = Competitor.objects.filter(insurance_valid=True, medical_certificate_valid=True)
        if selected_aircraft_type in dict(Competition._meta.get_field('type').choices):
            eligible_queryset = eligible_queryset.filter(aircraft_type=selected_aircraft_type)
        self.fields['competitors'].queryset = eligible_queryset

    def clean_competitors(self):
        competitors = self.cleaned_data.get('competitors')
        selected_aircraft_type = (self.cleaned_data.get('type') or '').strip().upper()
        if not competitors or not selected_aircraft_type:
            return competitors

        invalid = competitors.exclude(aircraft_type=selected_aircraft_type)
        if invalid.exists():
            raise forms.ValidationError('Selected competitors must match the competition aircraft type.')

        ineligible = competitors.filter(Q(insurance_valid=False) | Q(medical_certificate_valid=False))
        if ineligible.exists():
            raise forms.ValidationError('Selected competitors must have insurance and medical certificate marked as valid.')
        return competitors


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
    form = CompetitionAdminForm
    list_display = ('name', 'level', 'sub_level', 'aircraft_type', 'subtype', 'start_date', 'end_date', 'country', 'airfield', 'season')
    list_filter = ('level', 'sub_level', 'type', 'subtype', 'country', 'start_date')
    search_fields = ('name',)
    filter_horizontal = ('competitors', 'tasks', 'nfzs', 'decks')

    @admin.display(description='Aircraft type')
    def aircraft_type(self, obj):
        return obj.get_type_display()
