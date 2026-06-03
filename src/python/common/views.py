import requests

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

from .forms import LoginForm, UserSettingsForm
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


@login_required
def profile_settings_view(request):
    """Allow logged users to update personal information and password."""
    if request.method == 'POST':
        form = UserSettingsForm(request.POST, instance=request.user)
        if form.is_valid():
            updated_user = form.save()
            if form.cleaned_data.get('password1'):
                update_session_auth_hash(request, updated_user)
                messages.success(request, 'Your profile and password were updated.', extra_tags='popup')
            else:
                messages.success(request, 'Your profile was updated.', extra_tags='popup')
            return redirect('common:profile_settings')
        messages.error(request, 'Please correct the highlighted fields.')
    else:
        form = UserSettingsForm(instance=request.user)

    context = base_context(request)
    context['form'] = form
    return render(request, 'common/profile_settings.html', context)


def osm_tile_proxy(request, z, x, y):
    if min(z, x, y) < 0:
        raise Http404('Invalid tile coordinates.')

    tile_url = f'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
    try:
        upstream_response = requests.get(
            tile_url,
            headers={'User-Agent': 'SkyScore/1.0'},
            timeout=10,
        )
        upstream_response.raise_for_status()
    except requests.RequestException as exc:
        raise Http404('Tile unavailable.') from exc

    response = HttpResponse(
        upstream_response.content,
        content_type=upstream_response.headers.get('Content-Type', 'image/png'),
    )
    response['Cache-Control'] = 'public, max-age=3600'
    return response