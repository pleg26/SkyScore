from datetime import date

from django.conf import settings
from django.db import models

from common.models import Administrator
from database.models import Airfield, Country
from season.models import Season


class Competitor(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='competitors', null=True, blank=True)

    class Meta:
        verbose_name = 'Competitor'
        verbose_name_plural = 'Competitors'
        ordering = ['last_name', 'first_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Task(models.Model):
    name = models.CharField(max_length=120)

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ['name']

    def __str__(self):
        return self.name


class NFZ(models.Model):
    name = models.CharField(max_length=120)

    class Meta:
        verbose_name = 'No Fly Zone'
        verbose_name_plural = 'No Fly Zones'
        ordering = ['name']

    def __str__(self):
        return self.name


class Deck(models.Model):
    name = models.CharField(max_length=120)

    class Meta:
        verbose_name = 'Deck'
        verbose_name_plural = 'Decks'
        ordering = ['name']

    def __str__(self):
        return self.name


class Competition(models.Model):
    """Competition entry automatically linked to its season."""

    LEVEL_CHOICES = [
        ('WORLD', 'World'),
        ('NATIONAL', 'National'),
    ]

    SUB_LEVEL_CHOICES = [
        ('CHAMPIONSHIP', 'Championship'),
        ('CUP', 'Cup'),
        ('OPEN', 'Open'),
    ]

    name = models.CharField(max_length=120)
    level = models.CharField(max_length=20, choices=LEVEL_CHOICES)
    sub_level = models.CharField(max_length=20, choices=SUB_LEVEL_CHOICES)
    type = models.CharField(max_length=20, choices=Season.SEASON_TYPES)
    subtype = models.CharField(max_length=20, choices=Season.SEASON_SUBTYPES)
    start_date = models.DateField()
    end_date = models.DateField()
    country = models.ForeignKey(Country, on_delete=models.PROTECT, related_name='competitions')
    airfield = models.ForeignKey(Airfield, on_delete=models.PROTECT, related_name='competitions')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='competitions_created',
    )
    competitors = models.ManyToManyField(Competitor, related_name='competitions', blank=True)
    tasks = models.ManyToManyField(Task, related_name='competitions', blank=True)
    nfzs = models.ManyToManyField(NFZ, related_name='competitions', blank=True)
    decks = models.ManyToManyField(Deck, related_name='competitions', blank=True)
    season = models.ForeignKey(
        Season,
        on_delete=models.PROTECT,
        related_name='competitions',
        editable=False,
    )

    class Meta:
        verbose_name = 'Competition'
        verbose_name_plural = 'Competitions'
        ordering = ['start_date']

    def __str__(self):
        return f"{self.name} ({self.start_date})"

    def save(self, *args, **kwargs):
        year = self.start_date.year
        season, _ = Season.objects.get_or_create(
            type=self.type,
            subtype=self.subtype,
            year=year,
            defaults={
                'start_date': date(year, 1, 1),
                'end_date': date(year, 12, 31),
                'description': f'Auto-created season for {self.get_type_display()} {self.get_subtype_display()} {year}',
            },
        )

        Season.objects.exclude(pk=season.pk).filter(is_active=True).update(is_active=False)
        if not season.is_active:
            season.is_active = True
            season.save(update_fields=['is_active'])

        if self.created_by and self.created_by.role == 'ADM':
            administrator, _ = Administrator.objects.get_or_create(user=self.created_by)
            if administrator.active_season_id != season.id:
                administrator.active_season = season
                administrator.save(update_fields=['active_season'])

        self.season = season
        super().save(*args, **kwargs)
