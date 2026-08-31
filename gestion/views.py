from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.db.models import Q
from django.shortcuts import redirect, render

from .forms import (
    AnimalForm,
    CropForm,
    FrenchPasswordResetForm,
    HarvestForm,
    IncubatorForm,
    LoginForm,
    PlotForm,
    PoultryForm,
    SeasonForm,
    SignUpForm,
)
from .models import Animal, Crop, Harvest, Incubator, Notification, Plot, Poultry, Season


def home(request):
    crops = Crop.objects.count()
    animals = Animal.objects.count()
    plots = Plot.objects.count()
    incubators = Incubator.objects.count()
    return render(request, 'gestion/home.html', {
        'crops': crops,
        'animals': animals,
        'plots': plots,
        'incubators': incubators,
    })


@login_required
def dashboard(request):
    crops = Crop.objects.count()
    animals = Animal.objects.count()
    plots = Plot.objects.count()
    poultries = Poultry.objects.count()
    incubators = Incubator.objects.count()
    harvests = Harvest.objects.count()
    notifications = Notification.objects.order_by('-created_at')[:5]
    recent_activities = [
        {'title': 'Nouveau dashboard', 'description': 'Interface moderne prête à l\'emploi', 'icon': 'fas fa-chart-line'},
    ]
    preview_crops = Crop.objects.order_by('id')[:3]
    preview_incubators = Incubator.objects.order_by('-created_at')[:3]
    stats = [
        {'label': 'Cultures', 'value': crops, 'icon': 'fa-seedling'},
        {'label': 'Animaux', 'value': animals, 'icon': 'fa-cow'},
        {'label': 'Parcelles', 'value': plots, 'icon': 'fa-map'},
        {'label': 'Volailles', 'value': poultries, 'icon': 'fa-egg'},
        {'label': 'Incubations', 'value': incubators, 'icon': 'fa-egg'},
        {'label': 'Récoltes', 'value': harvests, 'icon': 'fa-tractor'},
    ]
    return render(request, 'gestion/dashboard.html', {
        'crops': crops,
        'animals': animals,
        'plots': plots,
        'poultries': poultries,
        'incubators': incubators,
        'harvests': harvests,
        'notifications': notifications,
        'recent_activities': recent_activities,
        'stats': stats,
        'preview_crops': preview_crops,
        'preview_incubators': preview_incubators,
    })


def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Compte créé avec succès.')
            return redirect('dashboard')
    else:
        form = SignUpForm()
    return render(request, 'registration/signup.html', {'form': form})


def custom_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('dashboard')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    return redirect('home')


@login_required
def crops_list(request):
    crops = Crop.objects.select_related('season').prefetch_related('plots').all()
    return render(request, 'gestion/crops.html', {'crops': crops})


@login_required
def crop_create(request):
    form = CropForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Culture ajoutée avec succès.')
        return redirect('crops')
    return render(request, 'gestion/culture_form.html', {'form': form, 'title': 'Ajouter une culture'})


@login_required
def crop_update(request, pk):
    crop = Crop.objects.get(pk=pk)
    form = CropForm(request.POST or None, instance=crop)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Culture mise à jour.')
        return redirect('crops')
    return render(request, 'gestion/culture_form.html', {'form': form, 'title': 'Modifier la culture'})


@login_required
def crop_delete(request, pk):
    crop = Crop.objects.get(pk=pk)
    crop.delete()
    messages.success(request, 'Culture supprimée.')
    return redirect('crops')


@login_required
def plots_list(request):
    plots = Plot.objects.all()
    return render(request, 'gestion/plots.html', {'plots': plots})


@login_required
def plot_create(request):
    form = PlotForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Parcelle ajoutée.')
        return redirect('plots')
    return render(request, 'gestion/plot_form.html', {'form': form, 'title': 'Ajouter une parcelle'})


@login_required
def plot_update(request, pk):
    plot = Plot.objects.get(pk=pk)
    form = PlotForm(request.POST or None, instance=plot)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Parcelle mise à jour.')
        return redirect('plots')
    return render(request, 'gestion/plot_form.html', {'form': form, 'title': 'Modifier la parcelle'})


@login_required
def plot_delete(request, pk):
    plot = Plot.objects.get(pk=pk)
    plot.delete()
    messages.success(request, 'Parcelle supprimée.')
    return redirect('plots')


@login_required
def seasons_list(request):
    seasons = Season.objects.all()
    return render(request, 'gestion/seasons.html', {'seasons': seasons})


@login_required
def season_create(request):
    form = SeasonForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Saison créée.')
        return redirect('seasons')
    return render(request, 'gestion/season_form.html', {'form': form, 'title': 'Créer une saison'})


@login_required
def harvests_list(request):
    harvests = Harvest.objects.select_related('crop').all()
    return render(request, 'gestion/harvests.html', {'harvests': harvests})


@login_required
def harvest_create(request):
    form = HarvestForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Récolte enregistrée.')
        return redirect('harvests')
    return render(request, 'gestion/harvest_form.html', {'form': form, 'title': 'Ajouter une récolte'})


@login_required
def animals_list(request):
    animals = Animal.objects.all()
    return render(request, 'gestion/animals.html', {'animals': animals})


@login_required
def animal_create(request):
    form = AnimalForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Animal ajouté.')
        return redirect('animals')
    return render(request, 'gestion/animal_form.html', {'form': form, 'title': 'Ajouter un animal'})


@login_required
def animal_update(request, pk):
    animal = Animal.objects.get(pk=pk)
    form = AnimalForm(request.POST or None, instance=animal)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Animal mis à jour.')
        return redirect('animals')
    return render(request, 'gestion/animal_form.html', {'form': form, 'title': 'Modifier l’animal'})


@login_required
def animal_delete(request, pk):
    animal = Animal.objects.get(pk=pk)
    animal.delete()
    messages.success(request, 'Animal supprimé.')
    return redirect('animals')


@login_required
def poultry_list(request):
    poultry = Poultry.objects.all()
    return render(request, 'gestion/aviculture.html', {'poultry': poultry})


@login_required
def poultry_create(request):
    form = PoultryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Données volailles enregistrées.')
        return redirect('poultry')
    return render(request, 'gestion/aviculture_form.html', {'form': form, 'title': 'Ajouter une volaille'})


@login_required
def incubators_list(request):
    incubators = Incubator.objects.all()
    return render(request, 'gestion/incubators.html', {'incubators': incubators})


@login_required
def incubator_create(request):
    form = IncubatorForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Incubation enregistrée (nombre d’œufs incubés saisi).')
        return redirect('incubators')
    return render(request, 'gestion/couveuse_form.html', {'form': form, 'title': 'Enregistrer une incubation'})


@login_required
def incubator_update(request, pk):
    incubator = Incubator.objects.get(pk=pk)
    form = IncubatorForm(request.POST or None, instance=incubator)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Incubation mise à jour.')
        return redirect('incubators')
    return render(request, 'gestion/couveuse_form.html', {'form': form, 'title': 'Modifier l’incubation'})


@login_required
def incubator_delete(request, pk):
    incubator = Incubator.objects.get(pk=pk)
    incubator.delete()
    messages.success(request, 'Incubation supprimée.')
    return redirect('incubators')


@login_required
def users_list(request):
    users = User.objects.select_related('profile').all()
    return render(request, 'gestion/users.html', {'users': users})


@login_required
def search(request):
    query = request.GET.get('q', '').strip()
    results = []
    if query:
        crops = Crop.objects.filter(
            Q(name__icontains=query) |
            Q(crop_type__icontains=query) |
            Q(estimated_production__icontains=query) |
            Q(status__icontains=query)
        )
        animals = Animal.objects.filter(
            Q(name__icontains=query) |
            Q(number__icontains=query) |
            Q(species__icontains=query) |
            Q(breed__icontains=query) |
            Q(health_status__icontains=query)
        )
        plots = Plot.objects.filter(
            Q(name__icontains=query) |
            Q(location__icontains=query) |
            Q(soil_type__icontains=query)
        )
        seasons = Season.objects.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )
        poultries = Poultry.objects.filter(
            Q(species__icontains=query) |
            Q(feed__icontains=query) |
            Q(egg_production__icontains=query) |
            Q(growth__icontains=query)
        )
        incubators = Incubator.objects.filter(
            Q(status__icontains=query) |
            Q(notes__icontains=query)
        )
        harvests = Harvest.objects.filter(
            Q(quantity__icontains=query) |
            Q(notes__icontains=query)
        )
        notifications = Notification.objects.filter(
            Q(title__icontains=query) |
            Q(message__icontains=query)
        )
        results = (
            [{'type': 'Culture', 'obj': obj} for obj in crops] +
            [{'type': 'Animal', 'obj': obj} for obj in animals] +
            [{'type': 'Parcelle', 'obj': obj} for obj in plots] +
            [{'type': 'Saison', 'obj': obj} for obj in seasons] +
            [{'type': 'Volaille', 'obj': obj} for obj in poultries] +
            [{'type': 'Incubation', 'obj': obj} for obj in incubators] +
            [{'type': 'Récolte', 'obj': obj} for obj in harvests] +
            [{'type': 'Notification', 'obj': obj} for obj in notifications]
        )
    return render(request, 'gestion/search_results.html', {'query': query, 'results': results})


@login_required
def notifications_view(request):
    items = Notification.objects.all()
    return render(request, 'gestion/notifications.html', {'items': items})
