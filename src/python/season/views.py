from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render

from common.models import Administrator
from common.utils.context import base_context

from .forms import SeasonForm
from .models import Season


def _can_manage_seasons(user):
    return user.is_authenticated and user.role in {'ADM', 'ORG'}


@login_required
@user_passes_test(_can_manage_seasons)
def season_select_view(request):
    seasons = Season.objects.order_by('-year', 'type', 'subtype')
    administrator = Administrator.objects.filter(user=request.user).select_related('active_season').first()
    context = base_context(request)
    context.update(
        {
            'seasons': seasons,
            'administrator': administrator,
            'page_title': 'Select active season',
            'show_actions': True,
        }
    )

    return render(
        request,
        'season/list.html',
        context,
    )


@login_required
@user_passes_test(_can_manage_seasons)
def season_active_view(request):
    administrator = Administrator.objects.filter(user=request.user).select_related('active_season').first()
    seasons = Season.objects.none()
    if administrator and administrator.active_season_id:
        seasons = Season.objects.filter(pk=administrator.active_season_id)

    context = base_context(request)
    context.update(
        {
            'seasons': seasons,
            'administrator': administrator,
            'page_title': 'Active season',
            'show_actions': False,
        }
    )
    return render(request, 'season/list.html', context)


@login_required
@user_passes_test(_can_manage_seasons)
def season_other_view(request):
    administrator = Administrator.objects.filter(user=request.user).select_related('active_season').first()
    seasons = Season.objects.order_by('-year', 'type', 'subtype')
    if administrator and administrator.active_season_id:
        seasons = seasons.exclude(pk=administrator.active_season_id)

    context = base_context(request)
    context.update(
        {
            'seasons': seasons,
            'administrator': administrator,
            'page_title': 'Other seasons',
            'show_actions': False,
        }
    )
    return render(request, 'season/list.html', context)


@login_required
@user_passes_test(_can_manage_seasons)
def season_update_view(request, pk):
    season = get_object_or_404(Season, pk=pk)

    if request.method == 'POST':
        form = SeasonForm(request.POST, instance=season)
        if form.is_valid():
            form.save()
            messages.success(request, 'Season updated successfully.')
            return redirect('season:select')
    else:
        form = SeasonForm(instance=season)

    context = base_context(request)
    context.update({'form': form, 'page_title': 'Edit season'})
    return render(request, 'season/form.html', context)


@login_required
@user_passes_test(_can_manage_seasons)
def season_activate_view(request, pk):
    if request.method != 'POST':
        return redirect('season:select')

    if request.user.role != 'ADM':
        messages.error(request, 'Only administrators can switch the active season.')
        return redirect('season:select')

    season = get_object_or_404(Season, pk=pk)
    Season.objects.exclude(pk=season.pk).filter(is_active=True).update(is_active=False)
    if not season.is_active:
        season.is_active = True
        season.save(update_fields=['is_active'])

    administrator, _ = Administrator.objects.get_or_create(user=request.user)
    administrator.active_season = season
    administrator.save(update_fields=['active_season'])

    messages.success(request, f'Active season set to {season}.')
    return redirect('season:select')
