import json

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

from common.utils.phone import get_country_dial_code, normalize_phone_number

from .models import Airfield, Competitor, Country


User = get_user_model()


class UserForm(forms.ModelForm):
    competitor_profile_sync = None

    change_password = forms.BooleanField(label='Change password', required=False)
    roles = forms.MultipleChoiceField(
        label='Additional roles',
        choices=User.ROLE_CHOICES,
        required=False,
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'roles-checkboxes'}),
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        min_length=8,
        required=False,
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        min_length=8,
        required=False,
    )

    class Meta:
        model = User
        fields = [
            'email',
            'role',
            'first_name',
            'last_name',
            'country',
            'phone_number',
            'date_of_birth',
            'sex',
            'fai_licence_number',
            'national_licence_number',
            'club',
            'is_active',
        ]
        labels = {
            'email': 'Email',
            'role': 'Role',
            'first_name': 'First name',
            'last_name': 'Last name',
            'country': 'Country',
            'phone_number': 'Phone',
            'date_of_birth': 'Date of birth',
            'sex': 'Sex',
            'fai_licence_number': 'FAI licence number',
            'national_licence_number': 'National licence number',
            'club': 'Club',
            'is_active': 'Active',
        }
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'type': 'tel', 'autocomplete': 'tel'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['roles'].choices = [choice for choice in User.ROLE_CHOICES if choice[0] != 'PUB']
        dial_map = {
            str(country.pk): get_country_dial_code(country)
            for country in Country.objects.all()
            if get_country_dial_code(country)
        }
        self.fields['country'].widget.attrs['data-country-dial-map'] = json.dumps(dial_map)
        base_order = [
            'email',
            'role',
            'first_name',
            'last_name',
            'country',
            'phone_number',
            'date_of_birth',
            'sex',
            'fai_licence_number',
            'national_licence_number',
            'club',
            'is_active',
            'roles',
        ]
        if self.instance and self.instance.pk:
            self.fields['roles'].initial = self.instance.roles
            self.fields['change_password'].initial = False
            self.fields['password1'].label = 'New password'
            self.fields['password2'].label = 'Confirm new password'
            self.fields['password1'].help_text = 'Leave blank to keep current password.'
            self.fields['password2'].help_text = 'Only required if a new password is entered.'
            self.order_fields(base_order + ['change_password', 'password1', 'password2'])
        else:
            self.fields.pop('change_password')
            self.order_fields(base_order + ['password1', 'password2'])

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        query = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_first_name(self):
        return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].strip()

    def clean_phone_number(self):
        raw_phone = self.cleaned_data.get('phone_number')
        country = self.cleaned_data.get('country') or getattr(self.instance, 'country', None)
        country_iso3 = getattr(country, 'iso3', None)
        dial_code = get_country_dial_code(country)
        return normalize_phone_number(raw_phone, country_iso3, dial_code=dial_code) or None

    def clean_fai_licence_number(self):
        return (self.cleaned_data.get('fai_licence_number') or '').strip() or None

    def clean_national_licence_number(self):
        return (self.cleaned_data.get('national_licence_number') or '').strip() or None

    def clean_club(self):
        return (self.cleaned_data.get('club') or '').strip() or None

    def clean(self):
        cleaned_data = super().clean()
        password1 = (cleaned_data.get('password1') or '').strip()
        password2 = (cleaned_data.get('password2') or '').strip()
        change_password = bool(cleaned_data.get('change_password'))

        if self.instance and self.instance.pk:
            if not change_password:
                password1 = ''
                password2 = ''
            else:
                if password1 and not password2:
                    raise ValidationError({'password2': 'Please confirm the new password.'})
                if password2 and not password1:
                    raise ValidationError({'password1': 'Please enter a new password before confirming it.'})
                if password1 and password2 and password1 != password2:
                    raise ValidationError({'password2': 'The two password fields do not match.'})
        else:
            if not password1 or not password2:
                raise ValidationError({'password2': 'Both password fields are required to create an account.'})
            if password1 != password2:
                raise ValidationError({'password2': 'The two password fields do not match.'})

        cleaned_data['password1'] = password1
        cleaned_data['password2'] = password2

        role = cleaned_data.get('role')
        extra_roles = cleaned_data.get('roles') or []

        normalized_extra_roles = []
        for extra_role in extra_roles:
            code = extra_role.strip().upper()
            if code == 'PIL':
                code = 'COMP'
            if code in dict(User.ROLE_CHOICES) and code not in normalized_extra_roles and code != role:
                normalized_extra_roles.append(code)
        cleaned_data['roles'] = normalized_extra_roles

        if role and self.instance and self.instance.pk:
            if hasattr(self.instance, 'administrator') and role != 'ADM':
                raise ValidationError({'role': 'A linked administrator account must keep the Administrator role.'})

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get('password1') or ''
        user.roles = self.cleaned_data.get('roles') or []
        self.competitor_profile_sync = None

        if password1:
            user.set_password(password1)

        if commit:
            user.save()

            # Keep competitor list in sync with explicit competitor role assignments.
            has_explicit_competitor_role = user.role == 'COMP' or 'COMP' in (user.roles or [])
            if has_explicit_competitor_role and not hasattr(user, 'competitor_profile'):
                Competitor.objects.create(
                    user=user,
                    first_name=user.first_name or '',
                    last_name=user.last_name or '',
                    email=user.email,
                    country=user.country,
                    phone_number=user.phone_number,
                    date_of_birth=user.date_of_birth,
                    sex=user.sex,
                    fai_licence_number=user.fai_licence_number,
                    national_licence_number=user.national_licence_number,
                    club=user.club,
                )
                self.competitor_profile_sync = 'created'
            if not has_explicit_competitor_role and hasattr(user, 'competitor_profile'):
                user.competitor_profile.delete()
                self.competitor_profile_sync = 'deleted'
            if has_explicit_competitor_role and hasattr(user, 'competitor_profile'):
                competitor = user.competitor_profile
                competitor.first_name = user.first_name or ''
                competitor.last_name = user.last_name or ''
                competitor.email = user.email
                competitor.country = user.country
                competitor.phone_number = user.phone_number
                competitor.date_of_birth = user.date_of_birth
                competitor.sex = user.sex
                competitor.fai_licence_number = user.fai_licence_number
                competitor.national_licence_number = user.national_licence_number
                competitor.club = user.club
                competitor.save()

        return user


class CompetitorForm(forms.ModelForm):
    initial_password = forms.CharField(
        label='Initial password',
        widget=forms.PasswordInput,
        min_length=8,
    )
    class Meta:
        model = Competitor
        fields = [
            'first_name',
            'last_name',
            'email',
            'country',
            'phone_number',
            'date_of_birth',
            'sex',
            'fai_licence_number',
            'national_licence_number',
            'club',
            'insurance_valid',
            'medical_certificate_valid',
            'competitor_type',
            'aircraft_type',
            'aircraft_class',
            'crew',
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
        labels = {
            'first_name': 'First name',
            'last_name': 'Last name',
            'email': 'Account email',
            'phone_number': 'Phone',
            'country': 'Country',
            'date_of_birth': 'Date of birth',
            'sex': 'Sex',
            'fai_licence_number': 'FAI licence number',
            'national_licence_number': 'National licence number',
            'club': 'Club',
            'insurance_valid': 'Insurance',
            'medical_certificate_valid': 'Medical certificate',
            'aircraft_type': 'Aircraft type',
            'aircraft_class': 'Aircraft class',
            'competitor_type': 'Competitor type',
            'crew': 'Crew partner',
            'cell_manufacturer': 'ULM cell manufacturer',
            'cell_model': 'ULM cell model',
            'engine_manufacturer': 'Engine manufacturer',
            'engine_model': 'Engine model',
            'cart_manufacturer': 'Cart manufacturer',
            'cart_model': 'Cart model',
            'wing_manufacturer': 'Wing manufacturer',
            'wing_model': 'Wing model',
            'wing_length': 'Wing length',
            'wing_surface': 'Wing surface',
            'wing_ptv': 'Wing PTV',
            'crew_weight': 'Crew weight',
        }
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'type': 'tel', 'autocomplete': 'tel'}),
            'wing_length': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'wing_surface': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'wing_ptv': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
            'crew_weight': forms.NumberInput(attrs={'step': '0.1', 'min': '0'}),
        }

    def _selected_competitor_type(self):
        valid_types = {choice[0] for choice in Competitor.COMPETITOR_TYPES}
        if self.is_bound:
            submitted_type = (self.data.get(self.add_prefix('competitor_type')) or '').strip().upper()
            if submitted_type in valid_types:
                return submitted_type

        initial_type = (self.initial.get('competitor_type') or '').strip().upper() if hasattr(self, 'initial') else ''
        if initial_type in valid_types:
            return initial_type

        if self.instance and self.instance.pk and self.instance.competitor_type in valid_types:
            return self.instance.competitor_type

        return 'PILOT'

    def _selected_aircraft_type(self):
        valid_types = {choice[0] for choice in Competitor.AIRCRAFT_TYPE_CHOICES}
        if self.is_bound:
            submitted_type = (self.data.get(self.add_prefix('aircraft_type')) or '').strip().upper()
            if submitted_type in valid_types:
                return submitted_type

        initial_type = (self.initial.get('aircraft_type') or '').strip().upper() if hasattr(self, 'initial') else ''
        if initial_type in valid_types:
            return initial_type

        if self.instance and self.instance.pk and self.instance.aircraft_type in valid_types:
            return self.instance.aircraft_type

        return 'PARAMOTOR'

    def _aircraft_class_choices_for_type(self, aircraft_type):
        allowed_codes = Competitor.AIRCRAFT_CLASSES_BY_TYPE.get(aircraft_type, set())
        return [
            (code, label)
            for code, label in Competitor.AIRCRAFT_CLASS_CHOICES
            if code in allowed_codes
        ]

    def _selected_aircraft_class(self):
        valid_classes = {choice[0] for choice in Competitor.AIRCRAFT_CLASS_CHOICES}
        if self.is_bound:
            submitted_class = (self.data.get(self.add_prefix('aircraft_class')) or '').strip().upper()
            if submitted_class in valid_classes:
                return submitted_class

        initial_class = (self.initial.get('aircraft_class') or '').strip().upper() if hasattr(self, 'initial') else ''
        if initial_class in valid_classes:
            return initial_class

        if self.instance and self.instance.pk and self.instance.aircraft_class in valid_classes:
            return self.instance.aircraft_class

        return ''

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not (self.instance and self.instance.pk):
            self.fields['competitor_type'].initial = 'PILOT'
        self.fields['competitor_type'].required = False
        self.fields['sex'].required = False
        self.fields['sex'].choices = [('', '---------')] + list(Competitor.SEX_CHOICES)
        dial_map = {
            str(country.pk): get_country_dial_code(country)
            for country in Country.objects.all()
            if get_country_dial_code(country)
        }
        self.fields['country'].widget.attrs['data-country-dial-map'] = json.dumps(dial_map)
        self.fields['crew'].required = False
        selected_aircraft_type = self._selected_aircraft_type()
        class_choices = self._aircraft_class_choices_for_type(selected_aircraft_type)
        self.fields['aircraft_class'].required = False
        self.fields['aircraft_class'].choices = [('', '---------')] + class_choices
        self.fields['aircraft_class'].help_text = ''
        self.fields['aircraft_class'].widget.attrs['data-aircraft-class-choices'] = json.dumps(
            {
                'PARAMOTOR': self._aircraft_class_choices_for_type('PARAMOTOR'),
                'MICROLIGHT': self._aircraft_class_choices_for_type('MICROLIGHT'),
            }
        )

        all_crew_options = []
        all_competitors = Competitor.objects.order_by('last_name', 'first_name')
        for candidate in all_competitors:
            if self.instance and self.instance.pk and candidate.pk == self.instance.pk:
                continue
            all_crew_options.append(
                {
                    'id': str(candidate.pk),
                    'label': str(candidate),
                    'type': candidate.competitor_type,
                    'aircraftType': candidate.aircraft_type,
                }
            )
        self.fields['crew'].widget.attrs['data-crew-options'] = json.dumps(all_crew_options)

        selected_competitor_type = self._selected_competitor_type()
        selected_aircraft_class = self._selected_aircraft_class()
        crew_allowed = bool(selected_aircraft_class) and selected_aircraft_class.endswith('2')
        required_partner_type = 'NAVIGATOR' if selected_competitor_type == 'PILOT' else 'PILOT'
        crew_queryset = Competitor.objects.none()
        if crew_allowed:
            crew_queryset = Competitor.objects.filter(
                competitor_type=required_partner_type,
                aircraft_type=selected_aircraft_type,
            ).order_by('last_name', 'first_name')
        if self.instance and self.instance.pk:
            crew_queryset = crew_queryset.exclude(pk=self.instance.pk)
        self.fields['crew'].queryset = crew_queryset
        self.fields['crew'].help_text = f'{required_partner_type.title()} only' if crew_allowed else 'Crew not available for class 1'

        # Backward compatibility: old records may have shared fields only on User.
        if self.instance and self.instance.pk and self.instance.user_id:
            linked_user = self.instance.user
            if not self.instance.email and linked_user.email:
                self.initial.setdefault('email', linked_user.email)
            if not self.instance.country_id and linked_user.country_id:
                self.initial.setdefault('country', linked_user.country_id)
            if not self.instance.phone_number and linked_user.phone_number:
                self.initial.setdefault('phone_number', linked_user.phone_number)
            if not self.instance.date_of_birth and linked_user.date_of_birth:
                self.initial.setdefault('date_of_birth', linked_user.date_of_birth)
            if not self.instance.sex and linked_user.sex:
                self.initial.setdefault('sex', linked_user.sex)

        if self.instance and self.instance.pk and self.instance.user_id:
            self.fields.pop('initial_password')
        else:
            self.fields['email'].required = True
            self.fields['initial_password'].required = True

    def clean_first_name(self):
        return self.cleaned_data['first_name'].strip()

    def clean_last_name(self):
        return self.cleaned_data['last_name'].strip()

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        query = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk and self.instance.user_id:
            query = query.exclude(pk=self.instance.user_id)
        if query.exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_phone_number(self):
        raw_phone = self.cleaned_data.get('phone_number')
        country = self.cleaned_data.get('country') or getattr(self.instance, 'country', None)
        country_iso3 = getattr(country, 'iso3', None)
        dial_code = get_country_dial_code(country)
        return normalize_phone_number(raw_phone, country_iso3, dial_code=dial_code) or None

    def clean_fai_licence_number(self):
        return (self.cleaned_data.get('fai_licence_number') or '').strip() or None

    def clean_national_licence_number(self):
        return (self.cleaned_data.get('national_licence_number') or '').strip() or None

    def clean_club(self):
        return (self.cleaned_data.get('club') or '').strip() or None

    def clean_initial_password(self):
        password = self.cleaned_data['initial_password']
        if len(password.strip()) < 8:
            raise ValidationError('The initial password must contain at least 8 characters.')
        return password

    def clean_aircraft_class(self):
        aircraft_class = self.cleaned_data.get('aircraft_class')
        aircraft_type = self.cleaned_data.get('aircraft_type') or self._selected_aircraft_type()
        if not aircraft_class:
            return None

        allowed = Competitor.AIRCRAFT_CLASSES_BY_TYPE.get(aircraft_type, set())
        if aircraft_class not in allowed:
            raise ValidationError('Selected aircraft class is not valid for the selected aircraft type.')
        return aircraft_class

    def clean(self):
        cleaned_data = super().clean()
        aircraft_class = cleaned_data.get('aircraft_class')
        crew = cleaned_data.get('crew')
        competitor_type = cleaned_data.get('competitor_type')

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
        if competitor_type == 'NAVIGATOR':
            for field in equipment_fields:
                cleaned_data[field] = None

        aircraft_type = cleaned_data.get('aircraft_type')
        aircraft_class = cleaned_data.get('aircraft_class') or ''
        is_microlight = aircraft_type == 'MICROLIGHT'
        is_paramotor = aircraft_type == 'PARAMOTOR'
        is_microlight_trike = is_microlight and aircraft_class.startswith('TRIKE')

        if is_paramotor:
            cleaned_data['cell_manufacturer'] = None
            cleaned_data['cell_model'] = None

        if is_microlight:
            cleaned_data['wing_length'] = None
            cleaned_data['wing_surface'] = None
            cleaned_data['wing_ptv'] = None
            cleaned_data['crew_weight'] = None

            if is_microlight_trike:
                cleaned_data['cell_manufacturer'] = None
                cleaned_data['cell_model'] = None
            else:
                cleaned_data['cart_manufacturer'] = None
                cleaned_data['cart_model'] = None
                cleaned_data['wing_manufacturer'] = None
                cleaned_data['wing_model'] = None

        if aircraft_class and aircraft_class.endswith('1') and crew:
            self.add_error('crew', 'Crew is not allowed for class 1 aircraft.')
        return cleaned_data

    def save(self, commit=True):
        competitor = super().save(commit=False)

        if not competitor.user_id:
            user = User.objects.create_user(
                email=competitor.email,
                password=self.cleaned_data['initial_password'],
                role='COMP',
                first_name=competitor.first_name,
                last_name=competitor.last_name,
                country=competitor.country,
                phone_number=competitor.phone_number,
                date_of_birth=competitor.date_of_birth,
                sex=competitor.sex,
                fai_licence_number=competitor.fai_licence_number,
                national_licence_number=competitor.national_licence_number,
                club=competitor.club,
            )
            competitor.user = user
        elif competitor.user_id:
            user = competitor.user
            user.email = competitor.email
            user.first_name = competitor.first_name
            user.last_name = competitor.last_name
            user.country = competitor.country
            user.phone_number = competitor.phone_number
            user.date_of_birth = competitor.date_of_birth
            user.sex = competitor.sex
            user.fai_licence_number = competitor.fai_licence_number
            user.national_licence_number = competitor.national_licence_number
            user.club = competitor.club
            user.save(
                update_fields=[
                    'email',
                    'first_name',
                    'last_name',
                    'country',
                    'phone_number',
                    'date_of_birth',
                    'sex',
                    'fai_licence_number',
                    'national_licence_number',
                    'club',
                ]
            )

        competitor.email = competitor.user.email if competitor.user_id else competitor.email
        competitor.phone_number = competitor.user.phone_number if competitor.user_id else competitor.phone_number

        if commit:
            competitor.save()

        return competitor


class CountryForm(forms.ModelForm):
    class Meta:
        model = Country
        fields = ['iso3', 'name', 'phone_dial_code']
        labels = {
            'iso3': 'ISO3',
            'name': 'Name',
            'phone_dial_code': 'Phone dial code',
        }

    def clean_iso3(self):
        return self.cleaned_data['iso3'].strip().upper()

    def clean_phone_dial_code(self):
        raw = (self.cleaned_data.get('phone_dial_code') or '').strip()
        if not raw:
            return None
        digits = ''.join(ch for ch in raw if ch.isdigit())
        if not digits:
            return None
        return f'+{digits}'


class AirfieldForm(forms.ModelForm):
    class Meta:
        model = Airfield
        fields = ['code', 'name', 'country', 'lat', 'lon', 'alt']
        labels = {
            'code': 'OACI Code',
            'name': 'Name',
            'country': 'Country',
            'lat': 'Latitude (decimal degrees)',
            'lon': 'Longitude (decimal degrees)',
            'alt': 'Altitude (feet)',
        }

    def clean_code(self):
        return self.cleaned_data['code'].strip().upper()
