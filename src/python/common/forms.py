from django import forms
from django.forms.widgets import PasswordInput

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