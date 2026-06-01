from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    """Custom user model for SkyScore."""

    ROLE_CHOICES = [
        ('ADM', 'Administrator'),
        ('ORG', 'Organizer'),
        ('PIL', 'Pilot'),
        ('JUD', 'Judge'),
        ('PUB', 'Public'),
    ]
    role = models.CharField(max_length=3, choices=ROLE_CHOICES, default='PUB')
    licence_number = models.CharField(max_length=50, blank=True, null=True)
    ulm_model = models.CharField(max_length=100, blank=True, null=True)  # For pilots

    def is_organizer(self):
        return self.role == 'ORG'

    def is_pilot(self):
        return self.role == 'PIL'

    def is_judge(self):
        return self.role == 'JUD'

class Administrator(models.Model):
    """Links an administrator user to an active season."""

    user = models.OneToOneField(User, on_delete=models.CASCADE, limit_choices_to={'role': 'ADM'})
    active_season = models.ForeignKey(
        'season.Season',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text="The currently active season for this administrator."
    )

    def __str__(self):
        return f"Admin: {self.user.username} (Active Season: {self.active_season})"