from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import LoginForm
from .utils.context import base_context

def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('common:home')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {email}!")
                return redirect('common:home')
            else:
                messages.error(request, "Invalid email or password.")
        else:
            messages.error(request, "Invalid email or password.")
    else:
        form = LoginForm()
    context = base_context(request)
    context['form'] = form
    return render(request, 'common/login.html', context)

def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('common:login')

@login_required
def home_view(request):
    """Home page view."""
    return render(request, 'common/home.html', base_context(request))