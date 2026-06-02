from django.test import TestCase
from django.urls import reverse

from common.models import User
from database.models import Airfield, Country


class DatabaseAccessTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name='France', iso3='FRA')
        self.admin = User.objects.create_user(
            email='admin.database@test.local',
            password='pwd',
            role='ADM',
        )
        self.organizer = User.objects.create_user(
            email='organizer.database@test.local',
            password='pwd',
            role='ORG',
        )

    def test_country_list_admin_allowed(self):
        self.client.force_login(self.admin)
        response = self.client.get(reverse('database:country_list'))
        self.assertEqual(response.status_code, 200)

    def test_country_list_non_admin_forbidden(self):
        self.client.force_login(self.organizer)
        response = self.client.get(reverse('database:country_list'))
        self.assertEqual(response.status_code, 302)

    def test_airfield_crud_create(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('database:airfield_create'),
            {
                'code': 'LFGX',
                'name': 'Test airfield',
                'country': self.country.id,
                'lat': 45.0,
                'lon': 6.0,
                'alt': 400,
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Airfield.objects.filter(code='LFGX').exists())
