import json

from django import forms
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.forms.widgets import PasswordInput

from database.models import Country

from .utils.phone import get_country_dial_code, normalize_phone_number


User = get_user_model()

class LoginForm(forms.Form):
    """Login form for SkyScore."""
    email = forms.EmailField(
        max_length=254,
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-input',
            'required': 'required',
            'autocomplete': 'email',
            'placeholder': 'Email registered in your account',
        })
    )
    password = forms.CharField(
        max_length=128,
        widget=PasswordInput(attrs={'class': 'form-input'}),
        label='Password'
    )


class UserSettingsForm(forms.ModelForm):
    change_password = forms.BooleanField(label='Change password', required=False)
    password1 = forms.CharField(
        label='New password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        min_length=8,
        required=False,
    )
    password2 = forms.CharField(
        label='Confirm new password',
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password'}),
        min_length=8,
        required=False,
    )

    class Meta:
        model = User
        fields = [
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
        labels = {
            'email': 'Email',
            'first_name': 'First name',
            'last_name': 'Last name',
            'country': 'Country',
            'phone_number': 'Phone',
            'date_of_birth': 'Date of birth',
            'sex': 'Sex',
            'fai_licence_number': 'FAI licence number',
            'national_licence_number': 'National licence number',
            'club': 'Club',
        }
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'phone_number': forms.TextInput(attrs={'type': 'tel', 'autocomplete': 'tel'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sex'].required = False
        self.fields['sex'].choices = [('', '---------')] + list(User.SEX_CHOICES)
        dial_map = {
            str(country.pk): get_country_dial_code(country)
            for country in Country.objects.all()
            if get_country_dial_code(country)
        }
        self.fields['country'].widget.attrs['data-country-dial-map'] = json.dumps(dial_map)
        self.order_fields([
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
            'change_password',
            'password1',
            'password2',
        ])

    def clean_email(self):
        email = (self.cleaned_data.get('email') or '').strip().lower()
        query = User.objects.filter(email__iexact=email)
        if self.instance and self.instance.pk:
            query = query.exclude(pk=self.instance.pk)
        if query.exists():
            raise ValidationError('A user with this email already exists.')
        return email

    def clean_first_name(self):
        return (self.cleaned_data.get('first_name') or '').strip()

    def clean_last_name(self):
        return (self.cleaned_data.get('last_name') or '').strip()

    def clean_phone_number(self):
        raw_phone = self.cleaned_data.get('phone_number')
        country = self.cleaned_data.get('country') or getattr(self.instance, 'country', None)
        dial_code = get_country_dial_code(country)
        country_iso3 = getattr(country, 'iso3', None)
        return normalize_phone_number(raw_phone, country_iso3, dial_code=dial_code) or None

    def clean_fai_licence_number(self):
        return (self.cleaned_data.get('fai_licence_number') or '').strip() or None

    def clean_national_licence_number(self):
        return (self.cleaned_data.get('national_licence_number') or '').strip() or None

    def clean_club(self):
        return (self.cleaned_data.get('club') or '').strip() or None

    def clean(self):
        cleaned_data = super().clean()
        change_password = bool(cleaned_data.get('change_password'))
        password1 = (cleaned_data.get('password1') or '').strip()
        password2 = (cleaned_data.get('password2') or '').strip()

        if not change_password:
            cleaned_data['password1'] = ''
            cleaned_data['password2'] = ''
            return cleaned_data

        if not password1:
            self.add_error('password1', 'Please enter a new password.')
        if not password2:
            self.add_error('password2', 'Please confirm the new password.')
        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'The two password fields do not match.')

        cleaned_data['password1'] = password1
        cleaned_data['password2'] = password2
        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        password1 = self.cleaned_data.get('password1') or ''
        if password1:
            user.set_password(password1)
        if commit:
            user.save()
            if hasattr(user, 'competitor_profile'):
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