from datetime import timedelta

from django import forms
from django.test import TestCase, override_settings
from django.utils import timezone

from signup.faculty.forms import FutureClassPeriodsForm


@override_settings(MAX_PERIOD_NUMBER=3)
class FutureClassPeriodsFormTestCase(TestCase):
    """Performs tests on :class:`signup.faculty.forms.FutureClassPeriodsForm`."""

    def test_form_choices(self):
        """Tests that the choices of the form are generated correctly based on the value
        of ``MAX_PERIOD_NUMBER`` in the project settings."""
        form = FutureClassPeriodsForm()
        visible_fields = form.visible_fields()

        # Checks that the first field is the date.
        self.assertEqual(visible_fields[0].label, "Date")
        self.assertTrue(isinstance(visible_fields[0].field, forms.DateField))
        # The initial value of the date field is tomorrow.
        self.assertEqual(
            visible_fields[0].value().date(), timezone.now().date() + timedelta(days=1)
        )

        # Checks that the integer fields are generated correctly.
        self.assertEqual(visible_fields[1].label, "Period 1")
        self.assertTrue(isinstance(visible_fields[1].field, forms.IntegerField))
        self.assertEqual(visible_fields[2].label, "Period 2")
        self.assertTrue(isinstance(visible_fields[2].field, forms.IntegerField))
        self.assertEqual(visible_fields[3].label, "Period 3")
        self.assertTrue(isinstance(visible_fields[3].field, forms.IntegerField))

        # Checks that the date field and the period fields are the only fields on the
        # form.
        self.assertEqual(len(visible_fields), 4)

    def test_form_validation(self):
        """Tests that the form validates complete and incomplete data correctly."""
        # All data is specified correctly, so everything should be fine.
        form = FutureClassPeriodsForm(
            data={"date": timezone.now(), "period_1": 1, "period_2": 0, "period_3": 1}
        )
        self.assertTrue(form.is_valid())

        # One or more missing fields should generate an error.
        form = FutureClassPeriodsForm(data={"date": timezone.now(), "period_1": 1})
        self.assertFalse(form.is_valid())

        # One or more missing fields should generate an error.
        form = FutureClassPeriodsForm(
            data={"period_1": 1, "period_2": 0, "period_3": 1}
        )
        self.assertFalse(form.is_valid())

        # An integer value lower than zero should generate an error.
        form = FutureClassPeriodsForm(
            data={"date": timezone.now(), "period_1": 1, "period_2": 0, "period_3": -1}
        )
        self.assertFalse(form.is_valid())
