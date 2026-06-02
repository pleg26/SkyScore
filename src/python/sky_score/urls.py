from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# Importe les handlers d'erreur
from common.utils.errors import error_400, error_403, error_404, error_500

# Déclare les handlers d'erreur
handler400 = error_400
handler403 = error_403
handler404 = error_404
handler500 = error_500

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(('common.urls', 'common'), namespace='common')),
    path('season/', include(('season.urls', 'season'), namespace='season')),
    path('database/', include(('database.urls', 'database'), namespace='database')),
]

# Pour servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)