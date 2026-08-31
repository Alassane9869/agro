from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm as DjangoPasswordResetForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Animal, Crop, Harvest, Incubator, Plot, Poultry, Season


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Nom d’utilisateur')
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)


class SignUpForm(UserCreationForm):
    username = forms.CharField(label='Nom d’utilisateur')
    email = forms.EmailField(required=True, label='Adresse e-mail')
    password1 = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirmation du mot de passe', widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class FrenchPasswordResetForm(DjangoPasswordResetForm):
    email = forms.EmailField(label='Adresse e-mail', required=True)


class CropForm(forms.ModelForm):
    class Meta:
        model = Crop
        fields = ['name', 'crop_type', 'planting_date', 'expected_harvest_date', 'area', 'status', 'estimated_production', 'photo', 'season', 'plots']
        widgets = {
            'planting_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_harvest_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PlotForm(forms.ModelForm):
    class Meta:
        model = Plot
        fields = ['name', 'area', 'location', 'soil_type']


class SeasonForm(forms.ModelForm):
    class Meta:
        model = Season
        fields = ['name', 'start_date', 'end_date', 'description']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }


class HarvestForm(forms.ModelForm):
    class Meta:
        model = Harvest
        fields = ['crop', 'harvest_date', 'quantity', 'notes']
        widgets = {
            'harvest_date': forms.DateInput(attrs={'type': 'date'}),
        }


class AnimalForm(forms.ModelForm):
    class Meta:
        model = Animal
        fields = ['name', 'number', 'species', 'breed', 'sex', 'age', 'birth_date', 'weight', 'health_status', 'vaccinations', 'treatments', 'photo']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }


class PoultryForm(forms.ModelForm):
    class Meta:
        model = Poultry
        fields = ['species', 'entries', 'exits', 'deaths', 'feed', 'egg_production', 'vaccination', 'growth', 'notes']


class IncubatorForm(forms.ModelForm):
    class Meta:
        model = Incubator
        fields = ['eggs_count', 'incubation_date', 'hatch_date', 'status', 'notes']
        labels = {
            'eggs_count': "Nombre d'œufs incubés",
            'incubation_date': "Date d'incubation",
            'hatch_date': "Date d'éclosion prévue",
            'status': 'Statut',
            'notes': 'Remarques',
        }
        widgets = {
            'incubation_date': forms.DateInput(attrs={'type': 'date'}),
            'hatch_date': forms.DateInput(attrs={'type': 'date'}),
        }
