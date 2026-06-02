from .localTime import localtime


def base_context(request):
    logged_admin = ''

    if request.user.is_authenticated:
        full_name = request.user.get_full_name().strip()
        logged_admin = full_name or request.user.email

    return {
        'current_date_time': localtime(),
        'tzinfo': 'Europe/Paris',
        'loggedAdmin': logged_admin,
    }
