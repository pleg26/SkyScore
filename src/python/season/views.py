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
def season_list_view(request):
    seasons = Season.objects.order_by('-year', 'type', 'subtype')
    administrator = Administrator.objects.filter(user=request.user).select_related('active_season').first()
    context = base_context(request)
    context.update(
        {
            'seasons': seasons,
            'administrator': administrator,
        }
    )

    return render(
        request,
        'season/list.html',
        context,
    )


@login_required
@user_passes_test(_can_manage_seasons)
def season_update_view(request, pk):
    season = get_object_or_404(Season, pk=pk)

    if request.method == 'POST':
        form = SeasonForm(request.POST, instance=season)
        if form.is_valid():
            form.save()
            messages.success(request, 'Season updated successfully.')
            return redirect('season:list')
    else:
        form = SeasonForm(instance=season)

    context = base_context(request)
    context.update({'form': form, 'page_title': 'Edit season'})
    return render(request, 'season/form.html', context)


@login_required
@user_passes_test(_can_manage_seasons)
def season_activate_view(request, pk):
    if request.method != 'POST':
        return redirect('season:list')

    if request.user.role != 'ADM':
        messages.error(request, 'Only administrators can switch the active season.')
        return redirect('season:list')

    season = get_object_or_404(Season, pk=pk)
    administrator, _ = Administrator.objects.get_or_create(user=request.user)
    administrator.active_season = season
    administrator.save(update_fields=['active_season'])

    messages.success(request, f'Active season set to {season}.')
    return redirect('season:list')
