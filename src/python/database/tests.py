from django.test import TestCase
from django.urls import reverse
from datetime import date
from django.core.exceptions import ValidationError

from common.models import User
from database.forms import CompetitorForm
from database.models import Airfield, CartModel, Competitor, Country, Manufacturer, ULMModel, WingModel


class DatabaseAccessTests(TestCase):
    def setUp(self):
        self.country = Country.objects.create(name='France', iso3='FRA')
        self.pilot = User.objects.create_user(
            email='pilot.database@test.local',
            password='pwd',
            role='COMP',
        )
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

    def test_competitor_crud_create(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('database:competitor_create'),
            {
                'first_name': 'Alice',
                'last_name': 'Martin',
                'aircraft_type': 'PARAMOTOR',
                'country': self.country.id,
                'email': 'alice.martin@test.local',
                'initial_password': 'StrongPassword123',
            },
        )
        self.assertEqual(response.status_code, 302)
        competitor = Competitor.objects.get(first_name='Alice', last_name='Martin')
        self.assertIsNotNone(competitor.user)
        self.assertEqual(competitor.user.email, 'alice.martin@test.local')
        self.assertEqual(competitor.user.role, 'COMP')
        self.assertTrue(competitor.user.check_password('StrongPassword123'))

    def test_competitor_delete_removes_user_when_only_competitor_role(self):
        self.client.force_login(self.admin)
        competitor_user = User.objects.create_user(
            email='only.comp@test.local',
            password='StrongPassword123',
            role='COMP',
        )
        competitor = Competitor.objects.create(
            first_name='Only',
            last_name='Competitor',
            competitor_type='PILOT',
            country=self.country,
            user=competitor_user,
        )

        response = self.client.post(reverse('database:competitor_delete', args=[competitor.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Competitor.objects.filter(pk=competitor.pk).exists())
        self.assertFalse(User.objects.filter(pk=competitor_user.pk).exists())

    def test_competitor_delete_keeps_user_and_removes_competitor_role_when_other_roles_exist(self):
        self.client.force_login(self.admin)
        mixed_user = User.objects.create_user(
            email='mixed.roles@test.local',
            password='StrongPassword123',
            role='ORG',
            roles=['COMP'],
        )
        competitor = Competitor.objects.create(
            first_name='Mixed',
            last_name='Roles',
            competitor_type='NAVIGATOR',
            country=self.country,
            user=mixed_user,
        )

        response = self.client.post(reverse('database:competitor_delete', args=[competitor.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Competitor.objects.filter(pk=competitor.pk).exists())

        mixed_user.refresh_from_db()
        self.assertEqual(mixed_user.role, 'ORG')
        self.assertNotIn('COMP', mixed_user.roles)

    def test_user_delete_forbidden_for_logged_user(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('database:user_delete', args=[self.admin.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(pk=self.admin.pk).exists())

    def test_user_delete_allowed_for_other_user(self):
        self.client.force_login(self.admin)
        response = self.client.post(reverse('database:user_delete', args=[self.organizer.pk]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(pk=self.organizer.pk).exists())

    def test_self_user_update_without_password_keeps_session(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('database:user_edit', args=[self.admin.pk]),
            {
                'email': self.admin.email,
                'role': 'ADM',
                'roles': ['COMP'],
                'first_name': 'AdminUpdated',
                'last_name': self.admin.last_name,
                'is_active': True,
                'password1': '',
                'password2': '',
            },
        )
        self.assertEqual(response.status_code, 302)

        # Session must still be authenticated after self-update without password change.
        follow_up = self.client.get(reverse('database:user_list'))
        self.assertEqual(follow_up.status_code, 200)

    def test_user_with_explicit_competitor_role_gets_competitor_profile(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('database:user_edit', args=[self.admin.pk]),
            {
                'email': self.admin.email,
                'role': 'ADM',
                'roles': ['COMP'],
                'first_name': self.admin.first_name,
                'last_name': self.admin.last_name,
                'is_active': self.admin.is_active,
                'password1': '',
                'password2': '',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.admin.refresh_from_db()
        self.assertTrue(hasattr(self.admin, 'competitor_profile'))

    def test_removing_explicit_competitor_role_deletes_competitor_profile(self):
        self.client.force_login(self.admin)

        # First, assign COMP role to auto-create profile.
        response = self.client.post(
            reverse('database:user_edit', args=[self.admin.pk]),
            {
                'email': self.admin.email,
                'role': 'ADM',
                'roles': ['COMP'],
                'first_name': self.admin.first_name,
                'last_name': self.admin.last_name,
                'is_active': self.admin.is_active,
                'password1': '',
                'password2': '',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.admin.refresh_from_db()
        self.assertTrue(hasattr(self.admin, 'competitor_profile'))

        # Then remove COMP role and verify profile is deleted.
        response = self.client.post(
            reverse('database:user_edit', args=[self.admin.pk]),
            {
                'email': self.admin.email,
                'role': 'ADM',
                'first_name': self.admin.first_name,
                'last_name': self.admin.last_name,
                'is_active': self.admin.is_active,
                'password1': '',
                'password2': '',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.admin.refresh_from_db()
        self.assertFalse(hasattr(self.admin, 'competitor_profile'))

    def test_user_crud_create(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('database:user_create'),
            {
                'email': 'judge.database@test.local',
                'role': 'JUD',
                'first_name': 'Jane',
                'last_name': 'Judge',
                'country': self.country.pk,
                'phone_number': '0611223344',
                'date_of_birth': '1990-01-01',
                'sex': 'F',
                'is_active': True,
                'password1': 'StrongPassword123',
                'password2': 'StrongPassword123',
            },
        )
        self.assertEqual(response.status_code, 302)
        created_user = User.objects.get(email='judge.database@test.local')
        self.assertEqual(created_user.role, 'JUD')
        self.assertTrue(created_user.check_password('StrongPassword123'))
        self.assertEqual(created_user.country_id, self.country.pk)
        self.assertEqual(created_user.phone_number, '+33611223344')

    def test_user_edit_syncs_shared_fields_to_competitor_profile(self):
        self.client.force_login(self.admin)
        competitor_user = User.objects.create_user(
            email='sync.user.to.comp@test.local',
            password='StrongPassword123',
            role='COMP',
            first_name='OldFirst',
            last_name='OldLast',
            date_of_birth=date(1980, 5, 5),
            sex='M',
        )
        competitor = Competitor.objects.create(
            first_name='OldFirst',
            last_name='OldLast',
            date_of_birth=date(1980, 5, 5),
            sex='M',
            competitor_type='PILOT',
            country=self.country,
            user=competitor_user,
        )

        response = self.client.post(
            reverse('database:user_edit', args=[competitor_user.pk]),
            {
                'email': competitor_user.email,
                'role': 'COMP',
                'first_name': 'NewFirst',
                'last_name': 'NewLast',
                'country': self.country.pk,
                'phone_number': '0611223344',
                'date_of_birth': '1992-03-04',
                'sex': 'F',
                'fai_licence_number': 'FAI-USER-1',
                'national_licence_number': 'NAT-USER-1',
                'club': 'User Sync Club',
                'is_active': True,
                'password1': '',
                'password2': '',
            },
        )
        self.assertEqual(response.status_code, 302)

        competitor.refresh_from_db()
        self.assertEqual(competitor.first_name, 'NewFirst')
        self.assertEqual(competitor.last_name, 'NewLast')
        self.assertEqual(competitor.email, competitor_user.email)
        self.assertEqual(competitor.country_id, self.country.pk)
        self.assertEqual(competitor.phone_number, '+33611223344')
        self.assertEqual(competitor.date_of_birth, date(1992, 3, 4))
        self.assertEqual(competitor.sex, 'F')
        self.assertEqual(competitor.fai_licence_number, 'FAI-USER-1')
        self.assertEqual(competitor.national_licence_number, 'NAT-USER-1')
        self.assertEqual(competitor.club, 'User Sync Club')

    def test_competitor_edit_syncs_shared_fields_to_user(self):
        self.client.force_login(self.admin)
        competitor_user = User.objects.create_user(
            email='sync.comp.to.user@test.local',
            password='StrongPassword123',
            role='COMP',
            first_name='PilotOld',
            last_name='PilotOld',
            date_of_birth=date(1985, 6, 7),
            sex='M',
        )
        competitor = Competitor.objects.create(
            first_name='PilotOld',
            last_name='PilotOld',
            date_of_birth=date(1985, 6, 7),
            sex='M',
            competitor_type='NAVIGATOR',
            country=self.country,
            user=competitor_user,
        )

        response = self.client.post(
            reverse('database:competitor_edit', args=[competitor.pk]),
            {
                'first_name': 'PilotNew',
                'last_name': 'PilotNew',
                'email': competitor_user.email,
                'aircraft_type': 'PARAMOTOR',
                'aircraft_class': 'PL2',
                'date_of_birth': '1991-08-09',
                'sex': 'F',
                'fai_licence_number': 'FAI-COMP-1',
                'national_licence_number': 'NAT-COMP-1',
                'club': 'Comp Sync Club',
                'insurance_valid': True,
                'medical_certificate_valid': True,
                'competitor_type': 'PILOT',
                'country': self.country.pk,
                'phone_number': '0611223344',
            },
        )
        self.assertEqual(response.status_code, 302)

        competitor_user.refresh_from_db()
        self.assertEqual(competitor_user.first_name, 'PilotNew')
        self.assertEqual(competitor_user.last_name, 'PilotNew')
        self.assertEqual(competitor_user.country_id, self.country.pk)
        self.assertEqual(competitor_user.phone_number, '+33611223344')
        self.assertEqual(competitor_user.date_of_birth, date(1991, 8, 9))
        self.assertEqual(competitor_user.sex, 'F')
        self.assertEqual(competitor_user.fai_licence_number, 'FAI-COMP-1')
        self.assertEqual(competitor_user.national_licence_number, 'NAT-COMP-1')
        self.assertEqual(competitor_user.club, 'Comp Sync Club')

    def test_user_password_update(self):
        self.client.force_login(self.admin)
        response = self.client.post(
            reverse('database:user_edit', args=[self.pilot.pk]),
            {
                'email': self.pilot.email,
                'role': self.pilot.role,
                'first_name': self.pilot.first_name,
                'last_name': self.pilot.last_name,
                'is_active': self.pilot.is_active,
                'change_password': True,
                'password1': 'NewStrongPassword123',
                'password2': 'NewStrongPassword123',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.pilot.refresh_from_db()
        self.assertTrue(self.pilot.check_password('NewStrongPassword123'))

    def test_user_update_ignores_password_fields_when_change_not_checked(self):
        self.client.force_login(self.admin)
        original_hash = self.pilot.password
        response = self.client.post(
            reverse('database:user_edit', args=[self.pilot.pk]),
            {
                'email': self.pilot.email,
                'role': self.pilot.role,
                'first_name': self.pilot.first_name,
                'last_name': self.pilot.last_name,
                'is_active': self.pilot.is_active,
                'password1': 'ShouldBeIgnored123',
                'password2': '',
            },
        )
        self.assertEqual(response.status_code, 302)
        self.pilot.refresh_from_db()
        self.assertEqual(self.pilot.password, original_hash)

    def test_navigator_cannot_have_equipment(self):
        manufacturer = Manufacturer.objects.create(name='Ozone')
        wing_model = WingModel.objects.create(name='Viper', manufacturer=manufacturer)
        competitor = Competitor(
            first_name='Navi',
            last_name='Gear',
            competitor_type='NAVIGATOR',
            country=self.country,
            wing_manufacturer=manufacturer,
            wing_model=wing_model,
        )

        with self.assertRaises(ValidationError):
            competitor.full_clean()

    def test_navigator_form_clears_equipment_fields(self):
        manufacturer = Manufacturer.objects.create(name='Fresh Breeze')
        wing_model = WingModel.objects.create(name='Bull', manufacturer=manufacturer)
        payload = {
            'first_name': 'Navi',
            'last_name': 'Form',
            'email': 'navi.form@test.local',
            'country': self.country.pk,
            'aircraft_type': 'PARAMOTOR',
            'aircraft_class': 'PL1',
            'competitor_type': 'NAVIGATOR',
            'initial_password': 'StrongPassword123',
            'wing_manufacturer': manufacturer.pk,
            'wing_model': wing_model.pk,
        }

        form = CompetitorForm(data=payload)
        self.assertTrue(form.is_valid(), form.errors)
        competitor = form.save()
        self.assertIsNone(competitor.wing_manufacturer)
        self.assertIsNone(competitor.wing_model)

    def test_crew_must_pair_pilot_and_navigator(self):
        first_pilot = Competitor.objects.create(
            first_name='Pilot',
            last_name='One',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='PILOT',
            country=self.country,
        )
        second_pilot = Competitor(
            first_name='Pilot',
            last_name='Two',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='PILOT',
            country=self.country,
            crew=first_pilot,
        )

        with self.assertRaises(ValidationError):
            second_pilot.full_clean()

    def test_crew_can_pair_pilot_with_navigator(self):
        pilot = Competitor.objects.create(
            first_name='Pilot',
            last_name='Solo',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='PILOT',
            country=self.country,
        )
        navigator = Competitor(
            first_name='Navi',
            last_name='Mate',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='NAVIGATOR',
            country=self.country,
            crew=pilot,
        )

        navigator.full_clean()

    def test_crew_field_filters_to_navigators_for_pilot_form(self):
        pilot = Competitor.objects.create(
            first_name='Pilot',
            last_name='Alpha',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='PILOT',
            country=self.country,
        )
        navigator = Competitor.objects.create(
            first_name='Navigator',
            last_name='Bravo',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='NAVIGATOR',
            country=self.country,
        )

        form = CompetitorForm(instance=pilot)
        self.assertIn(navigator, form.fields['crew'].queryset)
        self.assertNotIn(pilot, form.fields['crew'].queryset)

    def test_crew_field_excludes_other_aircraft_type(self):
        pilot = Competitor.objects.create(
            first_name='Pilot',
            last_name='Alpha',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='PILOT',
            country=self.country,
        )
        navigator_same_type = Competitor.objects.create(
            first_name='Navigator',
            last_name='Paramotor',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='NAVIGATOR',
            country=self.country,
        )
        navigator_other_type = Competitor.objects.create(
            first_name='Navigator',
            last_name='Microlight',
            aircraft_type='MICROLIGHT',
            aircraft_class='TRIKE2',
            competitor_type='NAVIGATOR',
            country=self.country,
        )

        form = CompetitorForm(instance=pilot)
        self.assertIn(navigator_same_type, form.fields['crew'].queryset)
        self.assertNotIn(navigator_other_type, form.fields['crew'].queryset)

    def test_crew_field_filters_to_pilots_for_navigator_form(self):
        pilot = Competitor.objects.create(
            first_name='Pilot',
            last_name='Alpha',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='PILOT',
            country=self.country,
        )
        navigator = Competitor.objects.create(
            first_name='Navigator',
            last_name='Bravo',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='NAVIGATOR',
            country=self.country,
        )

        form = CompetitorForm(instance=navigator)
        self.assertIn(pilot, form.fields['crew'].queryset)
        self.assertNotIn(navigator, form.fields['crew'].queryset)

    def test_crew_must_share_same_aircraft_type(self):
        pilot = Competitor.objects.create(
            first_name='Pilot',
            last_name='Alpha',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='PILOT',
            country=self.country,
        )
        navigator = Competitor(
            first_name='Navigator',
            last_name='Bravo',
            aircraft_type='MICROLIGHT',
            aircraft_class='TRIKE2',
            competitor_type='NAVIGATOR',
            country=self.country,
            crew=pilot,
        )

        with self.assertRaises(ValidationError):
            navigator.full_clean()

    def test_aircraft_class_must_match_aircraft_type(self):
        competitor = Competitor(
            first_name='Class',
            last_name='Mismatch',
            aircraft_type='PARAMOTOR',
            aircraft_class='TRIKE1',
            competitor_type='PILOT',
            country=self.country,
        )

        with self.assertRaises(ValidationError):
            competitor.full_clean()

    def test_crew_forbidden_for_class_1(self):
        pilot = Competitor.objects.create(
            first_name='Pilot',
            last_name='ClassOne',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL1',
            competitor_type='PILOT',
            country=self.country,
        )
        navigator = Competitor(
            first_name='Navigator',
            last_name='ClassOne',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL1',
            competitor_type='NAVIGATOR',
            country=self.country,
            crew=pilot,
        )

        with self.assertRaises(ValidationError):
            navigator.full_clean()

    def test_aircraft_class_form_choices_follow_aircraft_type(self):
        paramotor_form = CompetitorForm(initial={'aircraft_type': 'PARAMOTOR'})
        paramotor_codes = {code for code, _label in paramotor_form.fields['aircraft_class'].choices if code}
        self.assertEqual(paramotor_codes, {'PF1', 'PL1', 'PF2', 'PL2'})

        microlight_form = CompetitorForm(initial={'aircraft_type': 'MICROLIGHT'})
        microlight_codes = {code for code, _label in microlight_form.fields['aircraft_class'].choices if code}
        self.assertEqual(
            microlight_codes,
            {'TRIKE1', 'TRIKE2', 'MULTIAXIS1', 'MULTIAXIS2', 'AUTOGYRO1', 'AUTOGYRO2'},
        )

    def test_paramotor_cannot_use_aircraft_manufacturer_model(self):
        manufacturer = Manufacturer.objects.create(name='ICP')
        ulm_model = ULMModel.objects.create(name='Savannah', manufacturer=manufacturer)
        competitor = Competitor(
            first_name='Paramotor',
            last_name='InvalidConfig',
            aircraft_type='PARAMOTOR',
            aircraft_class='PL2',
            competitor_type='PILOT',
            country=self.country,
            cell_manufacturer=manufacturer,
            cell_model=ulm_model,
        )

        with self.assertRaises(ValidationError):
            competitor.full_clean()

    def test_microlight_non_trike_cannot_use_cart_fields(self):
        manufacturer = Manufacturer.objects.create(name='Fresh Breeze')
        cart_model = CartModel.objects.create(name='X-One', manufacturer=manufacturer)
        competitor = Competitor(
            first_name='Microlight',
            last_name='InvalidConfig',
            aircraft_type='MICROLIGHT',
            aircraft_class='MULTIAXIS2',
            competitor_type='PILOT',
            country=self.country,
            cart_manufacturer=manufacturer,
            cart_model=cart_model,
        )

        with self.assertRaises(ValidationError):
            competitor.full_clean()
