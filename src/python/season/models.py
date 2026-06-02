from django.db import models
from django.utils import timezone
from datetime import date


def default_start_date():
    today = timezone.localdate()
    return date(today.year, 1, 1)


def default_end_date():
    today = timezone.localdate()
    return date(today.year, 12, 31)

class Season(models.Model):
    """Represents a competition season (e.g., Paramotor Classic 2026)."""

    SEASON_TYPES = [
        ('PARAMOTOR', 'Paramotor'),
        ('MICROLIGHT', 'Microlight'),
    ]

    SEASON_SUBTYPES = [
        ('CLASSIC', 'Classic'),
        ('SLALOM', 'Slalom'),
        ('STOL', 'STOL'),
    ]

    type = models.CharField(max_length=20, choices=SEASON_TYPES)
    subtype = models.CharField(max_length=20, choices=SEASON_SUBTYPES)
    year = models.PositiveIntegerField()
    description = models.TextField(blank=True, help_text="Optional description of the season.")
    start_date = models.DateField(default=default_start_date)
    end_date = models.DateField(default=default_end_date)
    is_active = models.BooleanField(
        default=False,
        help_text="Only one season can be active at a time per administrator."
    )

    class Meta:
        unique_together = ('type', 'subtype', 'year')
        verbose_name = "Season"
        verbose_name_plural = "Seasons"

    def __str__(self):
        return f"{self.get_type_display()} {self.get_subtype_display()} {self.year}"
