from django import forms
from django.contrib.auth.forms import AuthenticationForm, PasswordResetForm as DjangoPasswordResetForm, UserCreationForm
from django.contrib.auth.models import User

from .models import Animal, Crop, Harvest, Incubator, Plot, Poultry, Season


class BaseStyledModelForm(forms.ModelForm):
    """Classe de base qui applique automatiquement le design moderne Bootstrap & Dark Mode."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            widget = field.widget
            widget_class = widget.__class__.__name__

            if isinstance(widget, (forms.Select, forms.SelectMultiple)):
                css_classes = 'form-select'
            elif isinstance(widget, forms.CheckboxInput):
                css_classes = 'form-check-input'
            elif isinstance(widget, forms.FileInput):
                css_classes = 'form-control form-control-file'
            else:
                css_classes = 'form-control'

            existing_classes = widget.attrs.get('class', '')
            widget.attrs['class'] = f"{existing_classes} {css_classes}".strip()
            
            # Placeholder agréable si non défini
            if not widget.attrs.get('placeholder') and field.label:
                widget.attrs['placeholder'] = f"Entrez {field.label.lower()}..."


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nom d’utilisateur',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Votre nom d\'utilisateur'})
    )
    password = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )


class SignUpForm(UserCreationForm):
    username = forms.CharField(
        label='Nom d’utilisateur',
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: moussa_agri'})
    )
    email = forms.EmailField(
        required=True,
        label='Adresse e-mail',
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@domaine.com'})
    )
    password1 = forms.CharField(
        label='Mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )
    password2 = forms.CharField(
        label='Confirmation du mot de passe',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '••••••••'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')


class FrenchPasswordResetForm(DjangoPasswordResetForm):
    email = forms.EmailField(
        label='Adresse e-mail',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'exemple@domaine.com'})
    )


class CropForm(BaseStyledModelForm):
    class Meta:
        model = Crop
        fields = ['name', 'crop_type', 'planting_date', 'expected_harvest_date', 'area', 'status', 'estimated_production', 'season', 'plots']
        labels = {
            'name': 'Nom de la culture',
            'crop_type': 'Type / Variété de culture',
            'planting_date': 'Date de semis / plantation',
            'expected_harvest_date': 'Date de récolte prévue',
            'area': 'Superficie cultivée (Hectares)',
            'status': 'Statut du cycle',
            'estimated_production': 'Production estimée (ex: 25 tonnes)',
            'season': 'Saison associée',
            'plots': 'Parcelles occupées',
        }
        widgets = {
            'planting_date': forms.DateInput(attrs={'type': 'date'}),
            'expected_harvest_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['expected_harvest_date'].required = False
        self.fields['estimated_production'].required = False
        self.fields['season'].required = False
        self.fields['plots'].required = False


class PlotForm(BaseStyledModelForm):
    class Meta:
        model = Plot
        fields = ['name', 'area', 'location', 'soil_type']
        labels = {
            'name': 'Nom de la parcelle',
            'area': 'Superficie (Hectares)',
            'location': 'Localisation / Coordonnées',
            'soil_type': 'Type de sol (Argileux, Sablonneux, Limoneux...)',
        }


class SeasonForm(BaseStyledModelForm):
    class Meta:
        model = Season
        fields = ['name', 'start_date', 'end_date', 'description']
        labels = {
            'name': 'Nom de la saison (ex: Hivernage 2026)',
            'start_date': 'Date de début',
            'end_date': 'Date de fin',
            'description': 'Description & Objectifs',
        }
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['description'].required = False


class HarvestForm(BaseStyledModelForm):
    class Meta:
        model = Harvest
        fields = ['crop', 'harvest_date', 'quantity', 'notes']
        labels = {
            'crop': 'Culture concernée',
            'harvest_date': 'Date de la récolte',
            'quantity': 'Quantité récoltée (ex: 4.5 tonnes)',
            'notes': 'Observations / Remarques',
        }
        widgets = {
            'harvest_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['notes'].required = False


class AnimalForm(BaseStyledModelForm):
    class Meta:
        model = Animal
        fields = ['name', 'number', 'species', 'breed', 'sex', 'age', 'birth_date', 'weight', 'health_status', 'vaccinations', 'treatments']
        labels = {
            'name': 'Nom / Surnom de l\'animal',
            'number': 'Numéro Matricule / Boucle',
            'species': 'Espèce animale',
            'breed': 'Race (ex: Zébu Peul, Balibali...)',
            'sex': 'Sexe',
            'age': 'Âge (en années)',
            'birth_date': 'Date de naissance approximative',
            'weight': 'Poids actuel (kg)',
            'health_status': 'État de santé',
            'vaccinations': 'Historique des vaccins',
            'treatments': 'Traitements en cours',
        }
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'vaccinations': forms.Textarea(attrs={'rows': 2}),
            'treatments': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['birth_date'].required = False
        self.fields['age'].required = False
        self.fields['vaccinations'].required = False
        self.fields['treatments'].required = False


class PoultryForm(BaseStyledModelForm):
    class Meta:
        model = Poultry
        fields = ['species', 'entries', 'exits', 'deaths', 'feed', 'egg_production', 'vaccination', 'growth', 'notes']
        labels = {
            'species': 'Type de volaille (Poules, Poussins, Pintades...)',
            'entries': 'Nombre d\'entrées / Naissances',
            'exits': 'Nombre de sorties / Ventes',
            'deaths': 'Nombre de pertes / Décès',
            'feed': 'Type d\'aliment distribué',
            'egg_production': 'Production d\'œufs (par jour)',
            'vaccination': 'Statut vaccinal',
            'growth': 'Stade de croissance',
            'notes': 'Observations complémentaires',
        }
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['feed'].required = False
        self.fields['egg_production'].required = False
        self.fields['vaccination'].required = False
        self.fields['growth'].required = False
        self.fields['notes'].required = False


class IncubatorForm(BaseStyledModelForm):
    class Meta:
        model = Incubator
        fields = ['eggs_count', 'incubation_date', 'hatch_date', 'status', 'notes']
        labels = {
            'eggs_count': "Nombre d'œufs placés en couveuse",
            'incubation_date': "Date de lancement de l'incubation",
            'hatch_date': "Date d'éclosion prévue (J+21)",
            'status': 'Statut du cycle',
            'notes': 'Remarques / Réglages température',
        }
        widgets = {
            'incubation_date': forms.DateInput(attrs={'type': 'date'}),
            'hatch_date': forms.DateInput(attrs={'type': 'date'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['hatch_date'].required = False
        self.fields['notes'].required = False
