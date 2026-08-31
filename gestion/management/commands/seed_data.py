from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from gestion.models import (
    Animal,
    Crop,
    Harvest,
    Incubator,
    Notification,
    Plot,
    Poultry,
    Season,
    UserProfile,
)


class Command(BaseCommand):
    help = 'Ajoute des données d\'exemple (cultures, animaux, incubations, etc.)'

    def handle(self, *args, **options):
        # === Saisons ===
        season_2025, _ = Season.objects.get_or_create(
            name='Saison 2025-2026',
            defaults={
                'start_date': date(2025, 10, 1),
                'end_date': date(2026, 4, 30),
                'description': 'Campagne agricole principale (saison sèche froide).',
            }
        )

        # === Parcelles ===
        plot1, _ = Plot.objects.get_or_create(
            name='Parcelle Nord',
            defaults={
                'area': 5.50,
                'location': 'Zone nord de l\'exploitation',
                'soil_type': 'Sablo-limoneux',
            }
        )
        plot2, _ = Plot.objects.get_or_create(
            name='Parcelle Sud',
            defaults={
                'area': 3.20,
                'location': 'Zone sud près de la rivière',
                'soil_type': 'Argilo-sableux',
            }
        )
        plot3, _ = Plot.objects.get_or_create(
            name='Jardin maraîcher',
            defaults={
                'area': 1.80,
                'location': 'À côté du bâtiment principal',
                'soil_type': 'Riche en humus',
            }
        )

        # === Cultures ===
        crops_data = [
            {'name': 'Maïs', 'crop_type': 'Céréale', 'planting_date': date(2025, 10, 15), 'expected_harvest_date': date(2026, 2, 15), 'area': 2.00, 'status': 'En croissance', 'estimated_production': '3,5 tonnes', 'season': season_2025, 'plots': [plot1]},
            {'name': 'Riz', 'crop_type': 'Céréale', 'planting_date': date(2025, 11, 20), 'expected_harvest_date': date(2026, 3, 20), 'area': 1.50, 'status': 'En croissance', 'estimated_production': '2,2 tonnes', 'season': season_2025, 'plots': [plot2]},
            {'name': 'Tomate', 'crop_type': 'Maraîchage', 'planting_date': date(2025, 12, 5), 'expected_harvest_date': date(2026, 3, 5), 'area': 0.50, 'status': 'Mûr', 'estimated_production': '600 kg', 'season': season_2025, 'plots': [plot3]},
            {'name': 'Comcombre', 'crop_type': 'Maraîchage', 'planting_date': date(2025, 12, 20), 'expected_harvest_date': date(2026, 3, 10), 'area': 0.30, 'status': 'En croissance', 'estimated_production': '350 kg', 'season': season_2025, 'plots': [plot3]},
            {'name': 'Gombo', 'crop_type': 'Maraîchage', 'planting_date': date(2026, 1, 10), 'expected_harvest_date': date(2026, 4, 10), 'area': 0.40, 'status': 'En croissance', 'estimated_production': '450 kg', 'season': season_2025, 'plots': [plot3]},
        ]
        crops = []
        for c in crops_data:
            crop, _ = Crop.objects.get_or_create(
                name=c['name'],
                defaults={
                    'crop_type': c['crop_type'],
                    'planting_date': c['planting_date'],
                    'expected_harvest_date': c['expected_harvest_date'],
                    'area': c['area'],
                    'status': c['status'],
                    'estimated_production': c['estimated_production'],
                    'season': c['season'],
                }
            )
            crop.plots.set(c['plots'])
            crops.append(crop)

        # === Récoltes ===
        Harvest.objects.get_or_create(
            crop=crops[2],
            defaults={
                'harvest_date': date(2026, 2, 25),
                'quantity': '240 kg',
                'notes': 'Première récolte de tomates.',
            }
        )

        # === Animaux ===
        animals_data = [
            {'name': 'Bellarine', 'number': 'BOV-001', 'species': 'Bovin', 'breed': 'Zébu', 'sex': 'Femelle', 'age': 3, 'birth_date': date(2022, 5, 10), 'weight': 350.00, 'health_status': 'En bonne santé', 'vaccinations': 'BCG (2025)', 'treatments': ''},
            {'name': 'Zourou', 'number': 'OVI-001', 'species': 'Ovin', 'breed': 'Mouton de case', 'sex': 'Mâle', 'age': 2, 'birth_date': date(2023, 3, 22), 'weight': 45.00, 'health_status': 'En bonne santé', 'vaccinations': 'Pasteurellose (2025)', 'treatments': ''},
            {'name': 'Capri', 'number': 'CAP-001', 'species': 'Caprin', 'breed': 'Chèvre du Sahel', 'sex': 'Femelle', 'age': 1, 'birth_date': date(2024, 8, 15), 'weight': 25.00, 'health_status': 'Traitement en cours', 'vaccinations': '', 'treatments': 'Déparasitage en cours'},
        ]
        for a in animals_data:
            Animal.objects.get_or_create(
                number=a['number'],
                defaults={
                    'name': a['name'],
                    'species': a['species'],
                    'breed': a['breed'],
                    'sex': a['sex'],
                    'age': a['age'],
                    'birth_date': a['birth_date'],
                    'weight': a['weight'],
                    'health_status': a['health_status'],
                    'vaccinations': a['vaccinations'],
                    'treatments': a['treatments'],
                }
            )

        # === Volailles ===
        poultry_data = [
            {'species': 'Poule pondeuse', 'entries': 120, 'exits': 5, 'deaths': 3, 'feed': 'Aliment pondeuse + maïs', 'egg_production': '85 œufs/jour', 'vaccination': 'Newcastle (2026)', 'growth': 'Stable', 'notes': 'Bon taux de ponte.'},
            {'species': 'Poulet', 'entries': 80, 'exits': 10, 'deaths': 2, 'feed': 'Aliment croissance', 'egg_production': '', 'vaccination': 'Gumboro (2026)', 'growth': 'En croissance', 'notes': 'Lot de chair en engraissement.'},
            {'species': 'Canard', 'entries': 30, 'exits': 0, 'deaths': 1, 'feed': 'Son de riz', 'egg_production': '12 œufs/jour', 'vaccination': '', 'growth': 'Stable', 'notes': ''},
        ]
        for p in poultry_data:
            Poultry.objects.get_or_create(
                species=p['species'],
                defaults={
                    'entries': p['entries'],
                    'exits': p['exits'],
                    'deaths': p['deaths'],
                    'feed': p['feed'],
                    'egg_production': p['egg_production'],
                    'vaccination': p['vaccination'],
                    'growth': p['growth'],
                    'notes': p['notes'],
                }
            )

        # === Incubations (couveuses) ===
        incubations_data = [
            {'eggs_count': 120, 'incubation_date': date(2026, 1, 25), 'hatch_date': date(2026, 2, 16), 'status': 'En incubation', 'notes': 'Œufs de poules pondeuses.'},
            {'eggs_count': 60, 'incubation_date': date(2026, 2, 1), 'hatch_date': date(2026, 2, 22), 'status': 'En incubation', 'notes': 'Œufs de pintade.'},
            {'eggs_count': 96, 'incubation_date': date(2026, 1, 10), 'hatch_date': date(2026, 2, 1), 'status': 'Éclosion prévue sous peu', 'notes': 'Contrôle de la température quotidien.'},
        ]
        for inc in incubations_data:
            Incubator.objects.get_or_create(
                incubation_date=inc['incubation_date'],
                defaults={
                    'eggs_count': inc['eggs_count'],
                    'hatch_date': inc['hatch_date'],
                    'status': inc['status'],
                    'notes': inc['notes'],
                }
            )

        # === Notifications ===
        notifications_data = [
            {'title': 'Éclosion imminente', 'message': 'La couveuse n°3 (96 œufs incubés) devrait éclore sous peu. Vérifiez l\'humidité.', 'notification_type': 'hatching'},
            {'title': 'Récolte de tomates', 'message': 'Les tomates de la parcelle Jardin maraîcher sont mûres. Prévoyez la récolte.', 'notification_type': 'harvest'},
            {'title': 'Vaccination à prévoir', 'message': 'Les poulets nécessitent la vaccination contre la maladie de Newcastle.', 'notification_type': 'vaccination'},
        ]
        for n in notifications_data:
            Notification.objects.get_or_create(
                title=n['title'],
                defaults={
                    'message': n['message'],
                    'notification_type': n['notification_type'],
                }
            )

        # === Utilisateur de démo ===
        demo_user, created = User.objects.get_or_create(
            username='demo',
            defaults={
                'email': 'demo@agrosedam.com',
                'is_staff': True,
            }
        )
        if created:
            demo_user.set_password('demo1234')
            demo_user.save()
        UserProfile.objects.get_or_create(
            user=demo_user,
            defaults={'role': 'admin', 'phone': '+226 70 00 00 00'}
        )

        self.stdout.write(self.style.SUCCESS('✔ Données d\'exemple ajoutées avec succès !'))
        self.stdout.write(self.style.SUCCESS('  - Compte démo : username "demo" / mot de passe "demo1234"'))