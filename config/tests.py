from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class LoginViewTests(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='demo',
            password='secret123',
        )

    def test_login_accepts_valid_credentials(self):
        response = self.client.post(reverse('connexion'), {
            'username': 'demo',
            'password': 'secret123',
        })

        self.assertRedirects(response, reverse('home'))
        self.assertTrue(response.wsgi_request.user.is_authenticated)

    def test_login_rejects_invalid_credentials(self):
        response = self.client.post(reverse('connexion'), {
            'username': 'demo',
            'password': 'wrong-password',
        })

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Identifiants invalides')
