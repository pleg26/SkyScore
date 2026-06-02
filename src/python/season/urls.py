from django.urls import path

from . import views

app_name = 'season'

urlpatterns = [
    path('', views.season_select_view, name='list'),
    path('select/', views.season_select_view, name='select'),
    path('active/', views.season_active_view, name='active'),
    path('others/', views.season_other_view, name='others'),
    path('<int:pk>/edit/', views.season_update_view, name='edit'),
    path('<int:pk>/activate/', views.season_activate_view, name='activate'),
] 
