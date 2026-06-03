from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class Country(models.Model):
    iso3 = models.CharField(max_length=3)
    name = models.CharField(max_length=100)
    phone_dial_code = models.CharField(max_length=8, blank=True, null=True)

    class Meta:
        verbose_name = 'Country'
        verbose_name_plural = 'Countries'
        ordering = ['iso3']
        db_table = 'competition_country'

    def __str__(self):
        text = self.iso3 + '-' + self.name
        if len(text) > 30:
            text = self.iso3 + '-' + self.name[0:26] + '...'
        return text


class Airfield(models.Model):
    code = models.CharField(max_length=6)
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.SET_DEFAULT, default=66, related_name='airfields')
    lon = models.FloatField(default=0)
    lat = models.FloatField(default=0)
    alt = models.IntegerField(default=0)

    class Meta:
        verbose_name = 'Airfield'
        verbose_name_plural = 'Airfields'
        ordering = ['country', 'code']
        db_table = 'competition_airfield'

    def __str__(self):
        text = self.code + ' - ' + self.name
        if len(text) > 30:
            text = text[0:30] + '...'
        return text


class Manufacturer(models.Model):
    name = models.CharField(max_length=100, unique=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class WingModel(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, related_name='wing_models')

    class Meta:
        ordering = ['manufacturer__name', 'name']
        unique_together = [('manufacturer', 'name')]

    def __str__(self):
        return f'{self.manufacturer.name} - {self.name}'


class CartModel(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, related_name='cart_models')

    class Meta:
        ordering = ['manufacturer__name', 'name']
        unique_together = [('manufacturer', 'name')]

    def __str__(self):
        return f'{self.manufacturer.name} - {self.name}'


class ULMModel(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, related_name='ulm_models')

    class Meta:
        ordering = ['manufacturer__name', 'name']
        unique_together = [('manufacturer', 'name')]

    def __str__(self):
        return f'{self.manufacturer.name} - {self.name}'


class EngineModel(models.Model):
    name = models.CharField(max_length=100)
    manufacturer = models.ForeignKey(Manufacturer, on_delete=models.PROTECT, related_name='engine_models')

    class Meta:
        ordering = ['manufacturer__name', 'name']
        unique_together = [('manufacturer', 'name')]

    def __str__(self):
        return f'{self.manufacturer.name} - {self.name}'


class Competitor(models.Model):
    AIRCRAFT_TYPE_CHOICES = [
        ('PARAMOTOR', 'Paramotor'),
        ('MICROLIGHT', 'Microlight'),
    ]

    AIRCRAFT_CLASS_CHOICES = [
        ('PF1', 'PF1'),
        ('PL1', 'PL1'),
        ('PF2', 'PF2'),
        ('PL2', 'PL2'),
        ('TRIKE1', 'Trike 1'),
        ('TRIKE2', 'Trike 2'),
        ('MULTIAXIS1', 'Multiaxis 1'),
        ('MULTIAXIS2', 'Multiaxis 2'),
        ('AUTOGYRO1', 'Autogyro 1'),
        ('AUTOGYRO2', 'Autogyro 2'),
    ]

    AIRCRAFT_CLASSES_BY_TYPE = {
        'PARAMOTOR': {'PF1', 'PL1', 'PF2', 'PL2'},
        'MICROLIGHT': {'TRIKE1', 'TRIKE2', 'MULTIAXIS1', 'MULTIAXIS2', 'AUTOGYRO1', 'AUTOGYRO2'},
    }

    COMPETITOR_TYPES = [
        ('PILOT', 'Pilot'),
        ('NAVIGATOR', 'Navigator'),
    ]
    SEX_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('X', 'Other / Prefer not to say'),
    ]

    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone_number = models.CharField(max_length=32, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    sex = models.CharField(max_length=1, choices=SEX_CHOICES, blank=True, null=True)
    fai_licence_number = models.CharField(max_length=80, blank=True, null=True)
    national_licence_number = models.CharField(max_length=80, blank=True, null=True)
    club = models.CharField(max_length=120, blank=True, null=True)
    insurance_valid = models.BooleanField(default=False)
    medical_certificate_valid = models.BooleanField(default=False)
    aircraft_type = models.CharField(max_length=20, choices=AIRCRAFT_TYPE_CHOICES, default='PARAMOTOR')
    aircraft_class = models.CharField(max_length=20, choices=AIRCRAFT_CLASS_CHOICES, blank=True, null=True)
    competitor_type = models.CharField(max_length=10, choices=COMPETITOR_TYPES, default='PILOT')
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='competitor_profile',
        null=True,
        blank=True,
    )
    country = models.ForeignKey(
        Country,
        on_delete=models.PROTECT,
        related_name='competitors',
        null=True,
        blank=True,
    )
    cell_manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        related_name='competitors_as_cell_manufacturer',
        null=True,
        blank=True,
    )
    cell_model = models.ForeignKey(
        ULMModel,
        on_delete=models.PROTECT,
        related_name='competitors_as_cell_model',
        null=True,
        blank=True,
    )
    engine_manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        related_name='competitors_as_engine_manufacturer',
        null=True,
        blank=True,
    )
    engine_model = models.ForeignKey(
        EngineModel,
        on_delete=models.PROTECT,
        related_name='competitors_as_engine_model',
        null=True,
        blank=True,
    )
    cart_manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        related_name='competitors_as_cart_manufacturer',
        null=True,
        blank=True,
    )
    cart_model = models.ForeignKey(
        CartModel,
        on_delete=models.PROTECT,
        related_name='competitors_as_cart_model',
        null=True,
        blank=True,
    )
    wing_manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.PROTECT,
        related_name='competitors_as_wing_manufacturer',
        null=True,
        blank=True,
    )
    wing_model = models.ForeignKey(
        WingModel,
        on_delete=models.PROTECT,
        related_name='competitors_as_wing_model',
        null=True,
        blank=True,
    )
    wing_length = models.FloatField(null=True, blank=True)
    wing_surface = models.FloatField(null=True, blank=True)
    wing_ptv = models.FloatField(null=True, blank=True)
    crew_weight = models.FloatField(null=True, blank=True)
    crew = models.OneToOneField(
        'self',
        on_delete=models.SET_NULL,
        related_name='crew_partner',
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name = 'Competitor'
        verbose_name_plural = 'Competitors'
        ordering = ['last_name', 'first_name']
        db_table = 'competition_competitor'

    def __str__(self):
        text = f'{self.first_name} {self.last_name}'.strip()
        if len(text) > 30:
            text = text[0:30] + '...'
        return text

    def clean(self):
        super().clean()
        if self.user and not self.user.has_explicit_role('COMP'):
            raise ValidationError({'user': 'The linked user must have the Competitor role.'})

        if self.crew_id:
            if self.pk and self.crew_id == self.pk:
                raise ValidationError({'crew': 'A competitor cannot be assigned as their own crew.'})

            if self.competitor_type == self.crew.competitor_type:
                raise ValidationError({'crew': 'Crew must link a Pilot to a Navigator.'})
            if self.aircraft_type != self.crew.aircraft_type:
                raise ValidationError({'crew': 'Crew members must share the same aircraft type.'})

        if self.aircraft_class and self.aircraft_class.endswith('1') and self.crew_id:
            raise ValidationError({'crew': 'Crew is not allowed for class 1 aircraft.'})

        allowed_classes = self.AIRCRAFT_CLASSES_BY_TYPE.get(self.aircraft_type, set())
        if self.aircraft_class and self.aircraft_class not in allowed_classes:
            raise ValidationError({'aircraft_class': 'Selected aircraft class is not valid for this aircraft type.'})

        equipment_fields = [
            'cell_manufacturer',
            'cell_model',
            'engine_manufacturer',
            'engine_model',
            'cart_manufacturer',
            'cart_model',
            'wing_manufacturer',
            'wing_model',
            'wing_length',
            'wing_surface',
            'wing_ptv',
            'crew_weight',
        ]
        has_equipment = any(getattr(self, field) for field in equipment_fields)
        if self.competitor_type == 'NAVIGATOR' and has_equipment:
            raise ValidationError(
                {
                    'competitor_type': 'Only pilots can have equipment fields filled.',
                }
            )

        # Enforce conditional equipment sets by aircraft type and class.
        is_microlight = self.aircraft_type == 'MICROLIGHT'
        is_paramotor = self.aircraft_type == 'PARAMOTOR'
        is_microlight_trike = is_microlight and (self.aircraft_class or '').startswith('TRIKE')

        paramotor_only_fields = ['wing_length', 'wing_surface', 'wing_ptv', 'crew_weight']
        aircraft_only_fields = ['cell_manufacturer', 'cell_model']
        trike_only_fields = ['cart_manufacturer', 'cart_model', 'wing_manufacturer', 'wing_model']

        if is_paramotor:
            invalid_fields = [field for field in aircraft_only_fields if getattr(self, field)]
            if invalid_fields:
                raise ValidationError({'aircraft_type': 'Paramotor competitors cannot use aircraft manufacturer/model fields.'})

        if is_microlight:
            invalid_fields = [field for field in paramotor_only_fields if getattr(self, field) is not None]
            if invalid_fields:
                raise ValidationError({'aircraft_type': 'Microlight competitors cannot use paramotor wing/crew-weight fields.'})

            if is_microlight_trike:
                invalid_fields = [field for field in aircraft_only_fields if getattr(self, field)]
                if invalid_fields:
                    raise ValidationError({'aircraft_class': 'Trike classes must use cart fields, not aircraft manufacturer/model.'})
            else:
                invalid_fields = [field for field in trike_only_fields if getattr(self, field)]
                if invalid_fields:
                    raise ValidationError(
                        {'aircraft_class': 'Non-trike microlight classes must use aircraft manufacturer/model fields.'}
                    )

        for field_name in ['wing_length', 'wing_surface', 'wing_ptv', 'crew_weight']:
            value = getattr(self, field_name)
            if value is not None and value <= 0:
                raise ValidationError({field_name: 'Value must be greater than 0.'})

    def save(self, *args, **kwargs):
        if self.sex is not None:
            normalized_sex = str(self.sex).strip().upper()
            if normalized_sex == '':
                normalized_sex = None
            allowed_sex = {choice[0] for choice in self.SEX_CHOICES}
            self.sex = normalized_sex if normalized_sex in allowed_sex else None
        super().save(*args, **kwargs)
