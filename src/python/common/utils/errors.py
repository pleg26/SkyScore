from django.shortcuts import render
from .localTime import localtime

def error_400(request, exception):
    """Custom 400 error page."""
    current_date_time = localtime()
    return render(request, 'common/errors.html', {
        'status_code': 400,
        'title': 'Bad Request',
        'message': 'The server cannot process your request due to a client error.',
        'current_date_time': current_date_time
    }, status=400)

def error_403(request, exception):
    """Custom 403 error page."""
    current_date_time = localtime()
    return render(request, 'common/errors.html', {
        'status_code': 403,
        'title': 'Forbidden',
        'message': 'You do not have permission to access this page.',
        'current_date_time': current_date_time
    }, status=403)

def error_404(request, exception):
    """Custom 404 error page."""
    current_date_time = localtime()
    return render(request, 'common/errors.html', {
        'status_code': 404,
        'title': 'Page Not Found',
        'message': 'The page you requested does not exist.',
        'current_date_time': current_date_time
    }, status=404)

def error_500(request):
    """Custom 500 error page."""
    current_date_time = localtime()
    return render(request, 'common/errors.html', {
        'status_code': 500,
        'title': 'Server Error',
        'message': 'An internal server error occurred.',
        'current_date_time': current_date_time
    }, status=500)