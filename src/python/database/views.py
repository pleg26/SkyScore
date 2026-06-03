from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models.deletion import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from common.utils.context import base_context
from common.utils.maps import airfield_map_from_form

from common.models import User

from .forms import AirfieldForm, CompetitorForm, CountryForm, UserForm
from .models import Airfield, Competitor, Country


def _can_manage_database(user):
    return user.is_authenticated and user.has_role('ADM')


def _render_competitor_page(request, form, *, show_create=False, show_edit=False, competitor=None):
    context = base_context(request)
    context.update(
        {
            'competitors': Competitor.objects.select_related('country', 'user').all(),
            'form': form,
            'competitor': competitor,
            'page_title': 'Competitor management',
            'show_create_form': show_create,
            'show_edit_form': show_edit,
            'aside_title': 'Modify competitor' if show_edit else 'Create competitor',
            'form_action': 'database:competitor_edit' if show_edit else 'database:competitor_create',
            'form_action_pk': competitor.pk if show_edit and competitor else None,
        }
    )
    return render(request, 'database/competitor_list.html', context)


def _render_user_page(request, form, *, show_create=False, show_edit=False, user=None):
    context = base_context(request)
    context.update(
        {
            'users': User.objects.select_related().all().order_by('role', 'email'),
            'form': form,
            'user_account': user,
            'logged_user_id': request.user.id,
            'is_edit_user_form': show_edit,
            'page_title': 'User management',
            'show_create_form': show_create,
            'show_edit_form': show_edit,
            'aside_title': 'Modify user' if show_edit else 'Create user',
            'form_action': 'database:user_edit' if show_edit else 'database:user_create',
            'form_action_pk': user.pk if show_edit and user else None,
        }
    )
    return render(request, 'database/user_list.html', context)


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
def user_list_view(request):
    return _render_user_page(request, UserForm(), show_create=True)


@login_required
@user_passes_test(_can_manage_database)
def user_create_view(request):
    if request.method == 'POST':
        form = UserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'User created successfully.')
            return redirect('database:user_list')
    else:
        form = UserForm()
    return _render_user_page(request, form, show_create=True)


@login_required
@user_passes_test(_can_manage_database)
def user_update_view(request, pk):
    user = get_object_or_404(User, pk=pk)
    is_self_update = request.user.pk == user.pk

    if request.method == 'POST':
        form = UserForm(request.POST, instance=user)
        if form.is_valid():
            updated_user = form.save()

            if is_self_update:
                # Keep session valid even when account data (including password) changes.
                update_session_auth_hash(request, updated_user)

            messages.success(request, 'User updated successfully.')

            if form.competitor_profile_sync == 'created':
                messages.info(
                    request,
                    'Competitor profile created automatically from Competitor role assignment.',
                    extra_tags='popup',
                )
            elif form.competitor_profile_sync == 'deleted':
                messages.info(
                    request,
                    'Competitor profile removed because Competitor role was removed.',
                    extra_tags='popup',
                )

            if is_self_update and not updated_user.has_role('ADM'):
                messages.info(request, 'Your account was updated and no longer has administrator access.')
                return redirect('common:home')

            return redirect('database:user_list')
    else:
        form = UserForm(instance=user)
    return _render_user_page(request, form, show_edit=True, user=user)


@login_required
@user_passes_test(_can_manage_database)
def user_delete_view(request, pk):
    user_to_delete = get_object_or_404(User, pk=pk)

    if request.method != 'POST':
        return redirect('database:user_list')

    if user_to_delete.pk == request.user.pk:
        messages.error(request, 'You cannot delete your own account while connected.')
        return redirect('database:user_list')

    try:
        user_to_delete.delete()
        messages.success(request, 'User deleted successfully.')
    except ProtectedError:
        messages.error(request, 'User cannot be deleted because it is referenced by other data.')
    return redirect('database:user_list')


@login_required
@user_passes_test(_can_manage_database)
def competitor_list_view(request):
    return _render_competitor_page(request, CompetitorForm(), show_create=True)


@login_required
@user_passes_test(_can_manage_database)
def competitor_create_view(request):
    if request.method == 'POST':
        form = CompetitorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Competitor created successfully.')
            return redirect('database:competitor_list')
    else:
        form = CompetitorForm()
    return _render_competitor_page(request, form, show_create=True)


@login_required
@user_passes_test(_can_manage_database)
def competitor_update_view(request, pk):
    competitor = get_object_or_404(Competitor, pk=pk)

    if request.method == 'POST':
        form = CompetitorForm(request.POST, instance=competitor)
        if form.is_valid():
            form.save()
            messages.success(request, 'Competitor updated successfully.')
            return redirect('database:competitor_list')
    else:
        form = CompetitorForm(instance=competitor)
    return _render_competitor_page(request, form, show_edit=True, competitor=competitor)


@login_required
@user_passes_test(_can_manage_database)
def competitor_delete_view(request, pk):
    competitor = get_object_or_404(Competitor, pk=pk)

    if request.method == 'POST':
        linked_user = competitor.user
        competitor.delete()

        if linked_user:
            explicit_roles = [linked_user.role] + list(linked_user.roles or [])
            explicit_roles = [role for role in explicit_roles if role and role != 'PUB']
            has_other_role_than_competitor = any(role != 'COMP' for role in explicit_roles)

            if not has_other_role_than_competitor:
                linked_user.delete()
                messages.success(
                    request,
                    'Competitor deleted successfully. Linked user account deleted (no other explicit role).',
                )
            else:
                remaining_roles = []
                for role in linked_user.roles or []:
                    if role != 'COMP' and role not in remaining_roles:
                        remaining_roles.append(role)

                if linked_user.role == 'COMP':
                    if remaining_roles:
                        linked_user.role = remaining_roles[0]
                        remaining_roles = remaining_roles[1:]
                    else:
                        linked_user.role = 'PUB'

                linked_user.roles = [role for role in remaining_roles if role != linked_user.role]
                linked_user.save(update_fields=['role', 'roles'])

                messages.success(
                    request,
                    'Competitor deleted successfully. Competitor role removed from linked user.',
                )
        else:
            messages.success(request, 'Competitor deleted successfully.')

        return redirect('database:competitor_list')

    return redirect('database:competitor_list')


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
