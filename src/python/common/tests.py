from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class CommonViewsTests(TestCase):
    def test_login_page_loads(self):
        response = self.client.get(reverse('common:login'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Login')

    def test_authenticated_user_redirected_from_login_to_home(self):
        user_model = get_user_model()
        user_model.objects.create_user(
            email='pilot1@example.com',
            password='StrongPassword123',
            role='PIL',
        )
        self.client.login(email='pilot1@example.com', password='StrongPassword123')

        response = self.client.get(reverse('common:login'))
        self.assertRedirects(response, reverse('common:home'))

    def test_home_requires_login(self):
        response = self.client.get(reverse('common:home'))
        self.assertEqual(response.status_code, 302)
