from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import Crop, Plot, Season


class AgroSedamViewsTests(TestCase):
    def test_home_page_is_available(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AgroSedam')

    def test_dashboard_renders_activity_chart(self):
        user = get_user_model().objects.create_user(username='testuser', password='StrongPass123!')
        self.client.force_login(user)

        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'activity-chart')

    def test_dashboard_requires_login(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_crop_creation_and_associations(self):
        season = Season.objects.create(name='Saison A', start_date='2026-01-01', end_date='2026-06-30')
        plot = Plot.objects.create(name='Parcelle 1', area=2.5, location='Bamako', soil_type='Argileux')
        crop = Crop.objects.create(
            name='Maïs',
            crop_type='Céréale',
            planting_date='2026-02-01',
            expected_harvest_date='2026-06-15',
            area=2.0,
            status='En croissance',
            estimated_production='500 kg',
            season=season,
        )
        crop.plots.add(plot)

        self.assertEqual(Crop.objects.count(), 1)
        self.assertEqual(crop.plots.count(), 1)
        self.assertEqual(crop.season.name, 'Saison A')

    def test_user_registration(self):
        response = self.client.post(reverse('signup'), {
            'username': 'fermier',
            'email': 'fermier@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(get_user_model().objects.filter(username='fermier').exists())
