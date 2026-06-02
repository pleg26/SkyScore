from urllib.error import URLError
from urllib.request import Request, urlopen

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponse
from django.shortcuts import redirect, render

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


def osm_tile_proxy(request, z, x, y):
    if min(z, x, y) < 0:
        raise Http404('Invalid tile coordinates.')

    tile_url = f'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
    upstream_request = Request(tile_url, headers={'User-Agent': 'SkyScore/1.0'})

    try:
        with urlopen(upstream_request, timeout=10) as upstream_response:
            content = upstream_response.read()
            content_type = upstream_response.headers.get('Content-Type', 'image/png')
    except URLError as exc:
        raise Http404('Tile unavailable.') from exc

    response = HttpResponse(content, content_type=content_type)
    response['Cache-Control'] = 'public, max-age=3600'
    return response