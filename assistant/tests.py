from django.test import TestCase
from django.urls import reverse


class AssistantViewsTests(TestCase):
    def test_assistant_home_page(self):
        response = self.client.get(reverse('assistant_home'))
        self.assertEqual(response.status_code, 200)

    def test_assistant_api_requires_login(self):
        response = self.client.post(reverse('assistant_api'), data={'message': 'Bonjour'}, content_type='application/json')
        self.assertEqual(response.status_code, 401)
