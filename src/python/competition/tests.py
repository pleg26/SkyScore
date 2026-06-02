from datetime import date

from django.contrib.auth import get_user_model
from django.test import TestCase

from common.models import Administrator
from season.models import Season

from .models import Airfield, Competition, Country


class CompetitionSeasonLinkTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name='France', iso3='FRA')
        self.airfield = Airfield.objects.create(code='LFGY', name='Belfort Chaux', country=self.country)

    def test_competition_uses_existing_season(self):
        season = Season.objects.create(
            type='PARAMOTOR',
            subtype='SLALOM',
            year=2026,
            start_date=date(2026, 1, 1),
            end_date=date(2026, 12, 31),
        )

        competition = Competition.objects.create(
            name='Championnat Slalom Juillet',
            level='WORLD',
            sub_level='CHAMPIONSHIP',
            type='PARAMOTOR',
            subtype='SLALOM',
            start_date=date(2026, 7, 10),
            end_date=date(2026, 7, 12),
            country=self.country,
            airfield=self.airfield,
        )

        self.assertEqual(competition.season_id, season.id)
        self.assertEqual(Season.objects.filter(type='PARAMOTOR', subtype='SLALOM', year=2026).count(), 1)
        season.refresh_from_db()
        self.assertTrue(season.is_active)

    def test_competition_creates_missing_season(self):
        self.assertFalse(Season.objects.filter(type='PARAMOTOR', subtype='SLALOM', year=2026).exists())

        competition = Competition.objects.create(
            name='Open Slalom Ete',
            level='NATIONAL',
            sub_level='OPEN',
            type='PARAMOTOR',
            subtype='SLALOM',
            start_date=date(2026, 7, 10),
            end_date=date(2026, 7, 11),
            country=self.country,
            airfield=self.airfield,
        )

        season = Season.objects.get(type='PARAMOTOR', subtype='SLALOM', year=2026)
        self.assertEqual(competition.season_id, season.id)
        self.assertEqual(season.start_date, date(2026, 1, 1))
        self.assertEqual(season.end_date, date(2026, 12, 31))
        self.assertTrue(season.is_active)

    def test_competition_by_admin_sets_admin_active_season(self):
        user_model = get_user_model()
        admin_user = user_model.objects.create_user(
            email='admin-competition@example.com',
            password='StrongPassword123',
            role='ADM',
        )

        competition = Competition.objects.create(
            name='Competition Admin Active Season',
            level='NATIONAL',
            sub_level='CUP',
            type='PARAMOTOR',
            subtype='SLALOM',
            start_date=date(2026, 7, 10),
            end_date=date(2026, 7, 12),
            country=self.country,
            airfield=self.airfield,
            created_by=admin_user,
        )

        administrator = Administrator.objects.get(user=admin_user)
        self.assertEqual(administrator.active_season_id, competition.season_id)

    def test_competition_default_ordering_by_start_date(self):
        early = Competition.objects.create(
            name='Early Competition',
            level='NATIONAL',
            sub_level='OPEN',
            type='PARAMOTOR',
            subtype='CLASSIC',
            start_date=date(2026, 6, 1),
            end_date=date(2026, 6, 2),
            country=self.country,
            airfield=self.airfield,
        )
        late = Competition.objects.create(
            name='Late Competition',
            level='WORLD',
            sub_level='CHAMPIONSHIP',
            type='MICROLIGHT',
            subtype='STOL',
            start_date=date(2026, 8, 1),
            end_date=date(2026, 8, 3),
            country=self.country,
            airfield=self.airfield,
        )

        self.assertEqual(list(Competition.objects.all()), [early, late])
