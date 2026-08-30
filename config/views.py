from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render


def home(request):
    return render(request, 'home.html')


def connexion(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'Bienvenue {user.username} !')
            return redirect('home')
        messages.error(request, 'Identifiants invalides')
    return render(request, 'connexion.html')


def cultures(request):
    return render(request, 'cultures.html')


def elevage(request):
    return render(request, 'elevage.html')
