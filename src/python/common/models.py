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
        ('COMP', 'Competitor'),
        ('JUD', 'Judge'),
        ('PUB', 'Public'),
    ]
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Other / Prefer not to say'),
    ]
    ROLE_HIERARCHY = {
        'PUB': set(),
        'COMP': {'PUB'},
        'JUD': {'PUB'},
        'ORG': {'PUB'},
        'ADM': {'ORG', 'JUD', 'COMP', 'PUB'},
    }

    role = models.CharField(max_length=4, choices=ROLE_CHOICES, default='PUB')
    roles = models.JSONField(default=list, blank=True)
    country = models.ForeignKey(
        'database.Country',
        on_delete=models.SET_NULL,
        related_name='users',
        null=True,
        blank=True,
    )
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True, null=True)
    fai_licence_number = models.CharField(max_length=80, blank=True, null=True)
    national_licence_number = models.CharField(max_length=80, blank=True, null=True)
    club = models.CharField(max_length=120, blank=True, null=True)
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

        self.role = (self.role or 'PUB').strip().upper()
        if self.role == 'PIL':
            self.role = 'COMP'

        normalized_roles = []
        for role in self.roles or []:
            candidate = str(role).strip().upper()
            if candidate == 'PIL':
                candidate = 'COMP'
            if candidate in dict(self.ROLE_CHOICES) and candidate not in normalized_roles and candidate != self.role:
                normalized_roles.append(candidate)
        self.roles = normalized_roles

        if self.sex is not None:
            normalized_sex = str(self.sex).strip().upper()
            if normalized_sex == '':
                normalized_sex = None
            allowed_sex = {choice[0] for choice in self.SEX_CHOICES}
            self.sex = normalized_sex if normalized_sex in allowed_sex else None

        super().save(*args, **kwargs)

    def effective_roles(self):
        roles = {self.role}
        roles.update(self.roles or [])
        expanded_roles = set(roles)
        for role in list(roles):
            expanded_roles.update(self.ROLE_HIERARCHY.get(role, set()))
        expanded_roles.add('PUB')
        return expanded_roles

    def has_role(self, role):
        return role in self.effective_roles()

    def has_explicit_role(self, role):
        role_code = (role or '').strip().upper()
        return self.role == role_code or role_code in (self.roles or [])

    def has_any_role(self, role_set):
        return any(self.has_role(role) for role in role_set)

    def is_organizer(self):
        return self.has_role('ORG')

    def is_pilot(self):
        return self.has_role('COMP')

    def is_judge(self):
        return self.has_role('JUD')

    def can_manage_database(self):
        return self.has_role('ADM')

    def can_manage_seasons(self):
        return self.has_any_role({'ADM', 'ORG'})

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