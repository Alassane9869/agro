from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('gestion.urls')),
    path('assistant/', include('assistant.urls')),
]
