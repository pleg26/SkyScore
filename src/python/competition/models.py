from datetime import date

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import m2m_changed
from django.dispatch import receiver

from common.models import Administrator
from database.models import Airfield, Country, Competitor
from season.models import Season


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

    def clean(self):
        super().clean()
        invalid_competitors = self.competitors.exclude(aircraft_type=self.type)
        if invalid_competitors.exists():
            raise ValidationError(
                {
                    'competitors': (
                        f'Only competitors with aircraft type {self.get_type_display()} can be linked to this competition.'
                    )
                }
            )

        ineligible_competitors = self.competitors.filter(
            models.Q(insurance_valid=False) | models.Q(medical_certificate_valid=False)
        )
        if ineligible_competitors.exists():
            raise ValidationError(
                {
                    'competitors': 'Competitors must have insurance and medical certificate marked as valid.'
                }
            )

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

        if self.created_by and self.created_by.has_role('ADM'):
            administrator, _ = Administrator.objects.get_or_create(user=self.created_by)
            if administrator.active_season_id != season.id:
                administrator.active_season = season
                administrator.save(update_fields=['active_season'])

        self.season = season
        super().save(*args, **kwargs)


@receiver(m2m_changed, sender=Competition.competitors.through)
def validate_competition_competitors_aircraft_type(sender, instance, action, pk_set, **kwargs):
    if action != 'pre_add' or not pk_set:
        return

    invalid_competitors = Competitor.objects.filter(pk__in=pk_set).exclude(aircraft_type=instance.type)
    if invalid_competitors.exists():
        raise ValidationError(
            f'Only competitors with aircraft type {instance.get_type_display()} can be linked to this competition.'
        )

    ineligible_competitors = Competitor.objects.filter(pk__in=pk_set).filter(
        models.Q(insurance_valid=False) | models.Q(medical_certificate_valid=False)
    )
    if ineligible_competitors.exists():
        raise ValidationError('Competitors must have insurance and medical certificate marked as valid.')
