from django.contrib import admin
from django.urls import path, include
from django.conf import settings 
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # This ensures that your Home, Prescription, Lab, and Grandma pages 
    # work from the base URL (e.g., 127.0.0.1:8000/)
    path('', include('api.urls')), 
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)