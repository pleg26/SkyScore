from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from common.utils.context import base_context
from common.utils.maps import airfield_map_from_form

from .forms import AirfieldForm, CountryForm
from .models import Airfield, Country


def _can_manage_database(user):
    return user.is_authenticated and user.role == 'ADM'


def _render_country_page(request, form, *, show_create=False, show_edit=False, country=None):
    context = base_context(request)
    context.update(
        {
            'countries': Country.objects.all(),
            'form': form,
            'country': country,
            'page_title': 'Country management',
            'show_create_form': show_create,
            'show_edit_form': show_edit,
            'aside_title': 'Modify country' if show_edit else 'Create country',
            'form_action': 'database:country_edit' if show_edit else 'database:country_create',
            'form_action_pk': country.pk if show_edit and country else None,
        }
    )
    return render(request, 'database/country_list.html', context)


def _render_airfield_page(request, form, *, show_create=False, show_edit=False, airfield=None):
    context = base_context(request)
    context.update(
        {
            'airfields': Airfield.objects.select_related('country').all(),
            'airfield_map': airfield_map_from_form(form),
            'form': form,
            'airfield': airfield,
            'page_title': 'Airfield management',
            'show_create_form': show_create,
            'show_edit_form': show_edit,
            'aside_title': 'Modify airfield' if show_edit else 'Create airfield',
            'form_action': 'database:airfield_edit' if show_edit else 'database:airfield_create',
            'form_action_pk': airfield.pk if show_edit and airfield else None,
        }
    )
    return render(request, 'database/airfield_list.html', context)


@login_required
@user_passes_test(_can_manage_database)
def country_list_view(request):
    return _render_country_page(request, CountryForm(), show_create=True)


@login_required
@user_passes_test(_can_manage_database)
def country_create_view(request):
    if request.method == 'POST':
        form = CountryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Country created successfully.')
            return redirect('database:country_list')
    else:
        form = CountryForm()
    return _render_country_page(request, form, show_create=True)


@login_required
@user_passes_test(_can_manage_database)
def country_update_view(request, pk):
    country = get_object_or_404(Country, pk=pk)

    if request.method == 'POST':
        form = CountryForm(request.POST, instance=country)
        if form.is_valid():
            form.save()
            messages.success(request, 'Country updated successfully.')
            return redirect('database:country_list')
    else:
        form = CountryForm(instance=country)
    return _render_country_page(request, form, show_edit=True, country=country)


@login_required
@user_passes_test(_can_manage_database)
def country_delete_view(request, pk):
    country = get_object_or_404(Country, pk=pk)

    if request.method == 'POST':
        try:
            country.delete()
            messages.success(request, 'Country deleted successfully.')
        except ProtectedError:
            messages.error(request, 'Country cannot be deleted because it is referenced by other data.')
        return redirect('database:country_list')

    return redirect('database:country_list')


@login_required
@user_passes_test(_can_manage_database)
def airfield_list_view(request):
    return _render_airfield_page(request, AirfieldForm(), show_create=True)


@login_required
@user_passes_test(_can_manage_database)
def airfield_create_view(request):
    if request.method == 'POST':
        form = AirfieldForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Airfield created successfully.')
            return redirect('database:airfield_list')
    else:
        form = AirfieldForm()
    return _render_airfield_page(request, form, show_create=True)


@login_required
@user_passes_test(_can_manage_database)
def airfield_update_view(request, pk):
    airfield = get_object_or_404(Airfield, pk=pk)

    if request.method == 'POST':
        form = AirfieldForm(request.POST, instance=airfield)
        if form.is_valid():
            form.save()
            messages.success(request, 'Airfield updated successfully.')
            return redirect('database:airfield_list')
    else:
        form = AirfieldForm(instance=airfield)
    return _render_airfield_page(request, form, show_edit=True, airfield=airfield)


@login_required
@user_passes_test(_can_manage_database)
def airfield_delete_view(request, pk):
    airfield = get_object_or_404(Airfield, pk=pk)

    if request.method == 'POST':
        try:
            airfield.delete()
            messages.success(request, 'Airfield deleted successfully.')
        except ProtectedError:
            messages.error(request, 'Airfield cannot be deleted because it is referenced by competitions.')
        return redirect('database:airfield_list')

    return redirect('database:airfield_list')
