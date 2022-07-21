from datetime import time

from constance import config
from constance.test import override_config
from django.test import TestCase
from django.urls import reverse

from signup.faculty.forms import SettingsForm
from signup.models import LibraryFacultyMember


class TestSettingsForm(TestCase):
    """Tests :class:`signup.faculty.forms.SettingsForm`."""

    def test_valid_form(self):
        """Tests submitting a valid form without any errors."""
        data_to_submit = {
            "max_period_number": 10,
            "force_open_sign_up_form": False,
            "sign_up_form_opens_time": time(1),
            "sign_up_form_closes_time": time(2),
            "lunch_periods_start": 3,
            "lunch_periods_end": 4,
        }

        form = SettingsForm(data=data_to_submit)
        self.assertTrue(form.is_valid())
        self.assertDictEqual(data_to_submit, form.cleaned_data)

    def test_invalid_form(self):
        """Tests submitting a valid form that produces error messages."""
        data_to_submit = {
            "max_period_number": 10,
            "force_open_sign_up_form": False,
            "sign_up_form_opens_time": time(2),
            "sign_up_form_closes_time": time(1),
            "lunch_periods_start": 4,
            "lunch_periods_end": 3,
        }

        form = SettingsForm(data=data_to_submit)
        self.assertFalse(form.is_valid())
        self.assertTrue("must come after the time that the form" in str(form.errors))
        self.assertTrue("must not come before" in str(form.errors))


@override_config(
    MAX_PERIOD_NUMBER=10,
    FORCE_OPEN_SIGN_UP_FORM=False,
    SIGN_UP_FORM_OPENS_TIME=time(5),
    SIGN_UP_FORM_CLOSES_TIME=time(7),
    LUNCH_PERIODS_START=3,
    LUNCH_PERIODS_END=4,
)
class TestSettingsView(TestCase):
    """Tests :class:`signup.faculty.views.SettingsFormView`."""

    def setUp(self):
        self.library_faculty_member = LibraryFacultyMember.objects.create_user(
            email="faculty@myhchs.org", password="12345"
        )
        self.client.force_login(self.library_faculty_member)

    def test_get_settings_form(self):
        """Tests that the form contains the existing values."""
        response = self.client.get(reverse("settings_form"))
        self.assertContains(response, "10")
        self.assertNotContains(response, "checked")
        self.assertContains(response, "5:00")
        self.assertContains(response, "7:00")
        self.assertContains(response, "3")
        self.assertContains(response, "4")

    def test_submit_settings_form(self):
        """Tests submitting a valid form. Ensures that the config values are updated
        correctly. Also tests that the template renders as expected."""
        response = self.client.post(
            reverse("settings_form"),
            {
                "max_period_number": 20,
                "force_open_sign_up_form": True,
                "sign_up_form_opens_time": time(1),
                "sign_up_form_closes_time": time(2),
                "lunch_periods_start": 6,
                "lunch_periods_end": 7,
            },
            follow=True,
        )

        # Checks that the form now contains the updated values.
        self.assertRedirects(response, reverse("settings_form"))
        self.assertContains(response, "20")
        self.assertContains(response, "checked")
        self.assertContains(response, "1:00")
        self.assertContains(response, "2:00")
        self.assertContains(response, "6")
        self.assertContains(response, "7")

        # Checks that the config values have been updated.
        self.assertEqual(config.MAX_PERIOD_NUMBER, 20)
        self.assertEqual(config.FORCE_OPEN_SIGN_UP_FORM, True)
        self.assertEqual(config.SIGN_UP_FORM_OPENS_TIME, time(1))
        self.assertEqual(config.SIGN_UP_FORM_CLOSES_TIME, time(2))
        self.assertEqual(config.LUNCH_PERIODS_START, 6)
        self.assertEqual(config.LUNCH_PERIODS_END, 7)

        # Checks that the message showed up.
        self.assertContains(response, "Settings saved successfully.")

        # Checks that the Bootstrap alert uses the right class.
        self.assertContains(response, "alert-success")
        self.assertNotContains(response, "alert-primary")
