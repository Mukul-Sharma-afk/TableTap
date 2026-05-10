from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
import os

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('tabletap/admin/', admin.site.urls),
    path('tabletap/', include('core.urls')),
    path('tabletap/accounts/', include('allauth.urls')),
]

# Needed for QR code generation on table_management page
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=os.path.join(settings.BASE_DIR, 'static'))

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)