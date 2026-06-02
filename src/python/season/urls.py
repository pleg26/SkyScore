from django.urls import path

from . import views

app_name = 'season'

urlpatterns = [
    path('', views.season_list_view, name='list'),
    path('<int:pk>/edit/', views.season_update_view, name='edit'),
    path('<int:pk>/activate/', views.season_activate_view, name='activate'),
]
