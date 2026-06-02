from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from common.models import Administrator

from .models import Season


class SeasonViewsTests(TestCase):
    def setUp(self):
        user_model = get_user_model()
        self.admin_user = user_model.objects.create_user(
            email='admin1@example.com',
            password='StrongPassword123',
            role='ADM',
        )
        self.organizer_user = user_model.objects.create_user(
            email='org1@example.com',
            password='StrongPassword123',
            role='ORG',
        )

        self.season_2026 = Season.objects.create(type='PARAMOTOR', subtype='CLASSIC', year=2026)
        self.season_2027 = Season.objects.create(type='PARAMOTOR', subtype='SLALOM', year=2027)

    def test_season_list_requires_login(self):
        response = self.client.get(reverse('season:list'))
        self.assertEqual(response.status_code, 302)

    def test_active_and_other_views_require_login(self):
        self.assertEqual(self.client.get(reverse('season:active')).status_code, 302)
        self.assertEqual(self.client.get(reverse('season:others')).status_code, 302)

    def test_admin_can_activate_season(self):
        self.client.login(email='admin1@example.com', password='StrongPassword123')

        response = self.client.post(reverse('season:activate', kwargs={'pk': self.season_2026.pk}))
        self.assertEqual(response.status_code, 302)

        admin = Administrator.objects.get(user=self.admin_user)
        self.assertEqual(admin.active_season_id, self.season_2026.id)

    def test_organizer_cannot_activate_season(self):
        self.client.login(email='org1@example.com', password='StrongPassword123')

        response = self.client.post(reverse('season:activate', kwargs={'pk': self.season_2026.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Administrator.objects.filter(user=self.organizer_user).exists())

    def test_admin_switches_active_season_without_global_side_effect(self):
        admin = Administrator.objects.create(user=self.admin_user, active_season=self.season_2026)
        self.client.login(email='admin1@example.com', password='StrongPassword123')

        self.client.post(reverse('season:activate', kwargs={'pk': self.season_2027.pk}))
        admin.refresh_from_db()

        self.assertEqual(admin.active_season_id, self.season_2027.id)

    def test_other_view_excludes_active_season(self):
        Administrator.objects.create(user=self.admin_user, active_season=self.season_2026)
        self.client.login(email='admin1@example.com', password='StrongPassword123')

        response = self.client.get(reverse('season:others'))
        self.assertEqual(response.status_code, 200)
        seasons = list(response.context['seasons'])
        self.assertIn(self.season_2027, seasons)
        self.assertNotIn(self.season_2026, seasons)
