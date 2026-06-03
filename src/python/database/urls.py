from django.urls import path

from . import views

app_name = 'database'

urlpatterns = [
    path('user/', views.user_list_view, name='user_list'),
    path('user/create/', views.user_create_view, name='user_create'),
    path('user/<int:pk>/edit/', views.user_update_view, name='user_edit'),
    path('user/<int:pk>/delete/', views.user_delete_view, name='user_delete'),
    path('competitor/', views.competitor_list_view, name='competitor_list'),
    path('competitor/create/', views.competitor_create_view, name='competitor_create'),
    path('competitor/<int:pk>/edit/', views.competitor_update_view, name='competitor_edit'),
    path('competitor/<int:pk>/delete/', views.competitor_delete_view, name='competitor_delete'),
    path('country/', views.country_list_view, name='country_list'),
    path('country/create/', views.country_create_view, name='country_create'),
    path('country/<int:pk>/edit/', views.country_update_view, name='country_edit'),
    path('country/<int:pk>/delete/', views.country_delete_view, name='country_delete'),
    path('airfield/', views.airfield_list_view, name='airfield_list'),
    path('airfield/create/', views.airfield_create_view, name='airfield_create'),
    path('airfield/<int:pk>/edit/', views.airfield_update_view, name='airfield_edit'),
    path('airfield/<int:pk>/delete/', views.airfield_delete_view, name='airfield_delete'),
]
