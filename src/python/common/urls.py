from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = 'common'

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='common:login', permanent=False), name='root'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('home/', views.home_view, name='home'),
    path('osm-tiles/<int:z>/<int:x>/<int:y>.png', views.osm_tile_proxy, name='osm_tile_proxy'),
]