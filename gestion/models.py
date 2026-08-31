from django.conf import settings
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Season(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Saison'
        verbose_name_plural = 'Saisons'
        ordering = ['-start_date']

    def __str__(self):
        return self.name


class Plot(models.Model):
    name = models.CharField(max_length=100)
    area = models.DecimalField(max_digits=6, decimal_places=2)
    location = models.CharField(max_length=150)
    soil_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Parcelle'
        verbose_name_plural = 'Parcelles'
        ordering = ['name']

    def __str__(self):
        return self.name


class Crop(models.Model):
    STATUS_CHOICES = [
        ('En croissance', 'En croissance'),
        ('Mûr', 'Mûr'),
        ('Récolté', 'Récolté'),
        ('Problème', 'Problème'),
    ]

    name = models.CharField(max_length=100)
    crop_type = models.CharField(max_length=100)
    planting_date = models.DateField()
    expected_harvest_date = models.DateField()
    area = models.DecimalField(max_digits=6, decimal_places=2)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='En croissance')
    estimated_production = models.CharField(max_length=100, blank=True)
    photo = models.CharField(max_length=255, blank=True)
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, related_name='crops')
    plots = models.ManyToManyField(Plot, blank=True, related_name='crops')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Culture'
        verbose_name_plural = 'Cultures'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Harvest(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='harvests')
    harvest_date = models.DateField()
    quantity = models.CharField(max_length=100)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Récolte'
        verbose_name_plural = 'Récoltes'
        ordering = ['-harvest_date']

    def __str__(self):
        return f"{self.crop.name} - {self.harvest_date}"


class Animal(models.Model):
    SPECIES_CHOICES = [
        ('Bovin', 'Bovin'),
        ('Ovin', 'Ovin'),
        ('Caprin', 'Caprin'),
        ('Porcin', 'Porcin'),
        ('Équin', 'Équin'),
        ('Lapin', 'Lapin'),
    ]
    SEX_CHOICES = [('Mâle', 'Mâle'), ('Femelle', 'Femelle')]
    HEALTH_CHOICES = [
        ('En bonne santé', 'En bonne santé'),
        ('À vacciner', 'À vacciner'),
        ('Traitement en cours', 'Traitement en cours'),
        ('Malade', 'Malade'),
    ]

    name = models.CharField(max_length=100)
    number = models.CharField(max_length=50, unique=True)
    species = models.CharField(max_length=30, choices=SPECIES_CHOICES)
    breed = models.CharField(max_length=100)
    sex = models.CharField(max_length=20, choices=SEX_CHOICES)
    age = models.IntegerField()
    birth_date = models.DateField()
    weight = models.DecimalField(max_digits=6, decimal_places=2)
    health_status = models.CharField(max_length=30, choices=HEALTH_CHOICES, default='En bonne santé')
    vaccinations = models.TextField(blank=True)
    treatments = models.TextField(blank=True)
    photo = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Animal'
        verbose_name_plural = 'Animaux'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.number})"


class Poultry(models.Model):
    SPECIES_CHOICES = [
        ('Poulet', 'Poulet'),
        ('Poule pondeuse', 'Poule pondeuse'),
        ('Canard', 'Canard'),
        ('Dinde', 'Dinde'),
        ('Pintade', 'Pintade'),
    ]

    species = models.CharField(max_length=30, choices=SPECIES_CHOICES)
    entries = models.IntegerField(default=0)
    exits = models.IntegerField(default=0)
    deaths = models.IntegerField(default=0)
    feed = models.CharField(max_length=100, blank=True)
    egg_production = models.CharField(max_length=100, blank=True)
    vaccination = models.CharField(max_length=100, blank=True)
    growth = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Volaille'
        verbose_name_plural = 'Volailles'
        ordering = ['-created_at']

    def __str__(self):
        return self.species


class Incubator(models.Model):
    eggs_count = models.IntegerField(verbose_name="Nombre d'œufs incubés")
    incubation_date = models.DateField(verbose_name="Date d'incubation")
    hatch_date = models.DateField(blank=True, null=True, verbose_name="Date d'éclosion prévue")
    status = models.CharField(max_length=50, default='En incubation', verbose_name='Statut')
    notes = models.TextField(blank=True, verbose_name='Remarques')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Incubation'
        verbose_name_plural = 'Incubations'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.eggs_count} œufs incubés le {self.incubation_date}"


class Notification(models.Model):
    TYPE_CHOICES = [
        ('vaccination', 'Vaccination'),
        ('harvest', 'Récolte'),
        ('hatching', 'Éclosion'),
        ('birth', 'Naissance'),
        ('disease', 'Maladie'),
    ]

    title = models.CharField(max_length=150)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Administrateur'),
        ('farmer', 'Agriculteur / Éleveur'),
    ]

    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='farmer')
    is_active = models.BooleanField(default=True)
    phone = models.CharField(max_length=20, blank=True)

    class Meta:
        verbose_name = 'Profil utilisateur'
        verbose_name_plural = 'Profils utilisateurs'

    def __str__(self):
        return f"{self.user.username} ({self.role})"


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
    else:
        UserProfile.objects.get_or_create(user=instance)
