import os
from pathlib import Path
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse, FileResponse
from django.conf import settings

BASE_DIR = Path(__file__).resolve().parent.parent

def manifest_view(request):
    manifest_path = BASE_DIR / 'static' / 'manifest.json'
    if manifest_path.exists():
        return FileResponse(open(manifest_path, 'rb'), content_type='application/manifest+json')
    return HttpResponse('{}', content_type='application/manifest+json')

def service_worker_view(request):
    sw_path = BASE_DIR / 'static' / 'service-worker.js'
    if sw_path.exists():
        response = FileResponse(open(sw_path, 'rb'), content_type='application/javascript')
        response['Service-Worker-Allowed'] = '/'
        return response
    return HttpResponse('', content_type='application/javascript')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('manifest.json', manifest_view, name='pwa_manifest'),
    path('service-worker.js', service_worker_view, name='pwa_service_worker'),
    path('', include('gestion.urls')),
    path('assistant/', include('assistant.urls')),
]
