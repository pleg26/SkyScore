from django.db import models
from django.utils import timezone

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
    start_date = models.DateField(default=timezone.now().replace(month=1, day=1))
    end_date = models.DateField(default=timezone.now().replace(month=12, day=31))
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

    def save(self, *args, **kwargs):
        """Ensure only one season is active at a time."""
        if self.is_active:
            # Deactivate all other seasons of the same type/subtype
            Season.objects.filter(is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)