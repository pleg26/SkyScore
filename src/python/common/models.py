from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.base_user import BaseUserManager
from django.db.models.functions import Lower


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The email field must be set')
        email = self.normalize_email(email).strip().lower()
        if not email:
            raise ValueError('The email field must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    """Custom user model for SkyScore."""

    username = None
    email = models.EmailField('email address', unique=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

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

    class Meta(AbstractUser.Meta):
        constraints = [
            models.UniqueConstraint(Lower('email'), name='common_user_email_lower_uniq'),
        ]

    def save(self, *args, **kwargs):
        # Enforce normalized email even if object is created/updated outside manager methods.
        if self.email is not None:
            self.email = self.__class__.objects.normalize_email(self.email).strip().lower()
        if not self.email:
            raise ValueError('The email field must be set')
        super().save(*args, **kwargs)

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
        return f"Admin: {self.user.email} (Active Season: {self.active_season})"