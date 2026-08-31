from django.contrib.auth import views as auth_views
from django.urls import path, reverse_lazy

from . import views
from .forms import FrenchPasswordResetForm

urlpatterns = [
    path('', views.home, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.custom_login, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('crops/', views.crops_list, name='crops'),
    path('crops/add/', views.crop_create, name='crop_create'),
    path('crops/<int:pk>/edit/', views.crop_update, name='crop_update'),
    path('crops/<int:pk>/delete/', views.crop_delete, name='crop_delete'),
    path('plots/', views.plots_list, name='plots'),
    path('plots/add/', views.plot_create, name='plot_create'),
    path('plots/<int:pk>/edit/', views.plot_update, name='plot_update'),
    path('plots/<int:pk>/delete/', views.plot_delete, name='plot_delete'),
    path('seasons/', views.seasons_list, name='seasons'),
    path('seasons/add/', views.season_create, name='season_create'),
    path('harvests/', views.harvests_list, name='harvests'),
    path('harvests/add/', views.harvest_create, name='harvest_create'),
    path('animals/', views.animals_list, name='animals'),
    path('animals/add/', views.animal_create, name='animal_create'),
    path('animals/<int:pk>/edit/', views.animal_update, name='animal_update'),
    path('animals/<int:pk>/delete/', views.animal_delete, name='animal_delete'),
    path('poultry/', views.poultry_list, name='poultry'),
    path('poultry/add/', views.poultry_create, name='poultry_create'),
    path('incubators/', views.incubators_list, name='incubators'),
    path('incubators/add/', views.incubator_create, name='incubator_create'),
    path('users/', views.users_list, name='users'),
    path('search/', views.search, name='search'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html', email_template_name='registration/password_reset_email.html', success_url=reverse_lazy('password_reset_done'), form_class=FrenchPasswordResetForm), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
]
