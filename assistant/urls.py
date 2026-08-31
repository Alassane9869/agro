from django.urls import path

from . import views

urlpatterns = [
    path('', views.assistant_home, name='assistant_home'),
    path('chat/', views.assistant_chat, name='assistant_chat'),
    path('api/', views.assistant_api, name='assistant_api'),
    path('history/', views.assistant_history, name='assistant_history'),
]
