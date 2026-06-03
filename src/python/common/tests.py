from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from datetime import date

from database.models import Competitor, Country


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
            role='COMP',
        )
        self.client.login(email='pilot1@example.com', password='StrongPassword123')

        response = self.client.get(reverse('common:login'))
        self.assertRedirects(response, reverse('common:home'))

    def test_home_requires_login(self):
        response = self.client.get(reverse('common:home'))
        self.assertEqual(response.status_code, 302)

    def test_profile_settings_syncs_linked_competitor(self):
        user_model = get_user_model()
        country = Country.objects.create(name='France', iso3='FRA')
        user = user_model.objects.create_user(
            email='profile.sync@test.local',
            password='StrongPassword123',
            role='COMP',
            first_name='Old',
            last_name='Name',
            date_of_birth=date(1980, 1, 1),
            sex='M',
        )
        competitor = Competitor.objects.create(
            first_name='Old',
            last_name='Name',
            date_of_birth=date(1980, 1, 1),
            sex='M',
            competitor_type='PILOT',
            country=country,
            user=user,
        )

        self.client.force_login(user)
        response = self.client.post(
            reverse('common:profile_settings'),
            {
                'email': user.email,
                'first_name': 'New',
                'last_name': 'Identity',
                'country': country.pk,
                'phone_number': '0611223344',
                'date_of_birth': '1993-04-05',
                'sex': 'F',
                'fai_licence_number': 'FAI-12345',
                'national_licence_number': 'NAT-67890',
                'club': 'Aero Club Test',
                'password1': '',
                'password2': '',
            },
        )
        self.assertEqual(response.status_code, 302)

        competitor.refresh_from_db()
        self.assertEqual(competitor.first_name, 'New')
        self.assertEqual(competitor.last_name, 'Identity')
        self.assertEqual(competitor.email, user.email)
        self.assertEqual(competitor.country_id, country.pk)
        self.assertEqual(competitor.phone_number, '+33611223344')
        self.assertEqual(competitor.date_of_birth, date(1993, 4, 5))
        self.assertEqual(competitor.sex, 'F')
        self.assertEqual(competitor.fai_licence_number, 'FAI-12345')
        self.assertEqual(competitor.national_licence_number, 'NAT-67890')
        self.assertEqual(competitor.club, 'Aero Club Test')
