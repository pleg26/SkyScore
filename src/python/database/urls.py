from django.urls import path

from . import views

app_name = 'database'

urlpatterns = [
    path('country/', views.country_list_view, name='country_list'),
    path('country/create/', views.country_create_view, name='country_create'),
    path('country/<int:pk>/edit/', views.country_update_view, name='country_edit'),
    path('country/<int:pk>/delete/', views.country_delete_view, name='country_delete'),
    path('airfield/', views.airfield_list_view, name='airfield_list'),
    path('airfield/create/', views.airfield_create_view, name='airfield_create'),
    path('airfield/<int:pk>/edit/', views.airfield_update_view, name='airfield_edit'),
    path('airfield/<int:pk>/delete/', views.airfield_delete_view, name='airfield_delete'),
]
