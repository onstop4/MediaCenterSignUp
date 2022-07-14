from datetime import timedelta

from django import forms
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from signup.faculty.forms import FutureClassPeriodsForm
from signup.models import ClassPeriod, LibraryFacultyMember


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


@override_settings(MAX_PERIOD_NUMBER=3)
class FutureClassPeriodsViewTestCase(TestCase):
    """Performs tests on :class:`signup.faculty.forms.FutureClassPeriodsFormView`."""

    def setUp(self):
        self.library_faculty_member = LibraryFacultyMember.objects.create_user(
            email="faculty@myhchs.org"
        )
        self.client.force_login(self.library_faculty_member)

    def test_form_new_future_periods(self):
        """Tests getting the form for a new set of ClassPeriods. Also tests submitting a
        response."""
        date = timezone.now().date() + timedelta(days=3)

        # Checks that the form has generated fields according to the value of
        # MAX_PERIOD_NUMBER in the project settings.
        response = self.client.get(reverse("future_class_periods_new"))
        self.assertContains(response, "Period 1")
        self.assertContains(response, "Period 2")
        self.assertContains(response, "Period 3")
        self.assertNotContains(response, "Period 4")

        # Checks that the form contains the initial value of zero.
        self.assertContains(response, "0")

        # Checks that the form is submitted without any errors. Uses a date 3 days into
        # the future.
        response = self.client.post(
            reverse("future_class_periods_new"),
            {
                "date": str(date),
                "period_1": "10",
                "period_2": "10",
                "period_3": "10",
            },
        )
        self.assertRedirects(response, reverse("future_class_periods_list"))

        # Checks that the only ClassPeriod objects that exist are the ones created
        # above.
        periods = ClassPeriod.objects.filter(date=date)
        self.assertEqual(periods.count(), 3)

        # Checks that all the ClassPeriods have the correct value for the
        # max_student_count field.
        self.assertEqual(periods[0].max_student_count, 10)
        self.assertEqual(periods[1].max_student_count, 10)
        self.assertEqual(periods[2].max_student_count, 10)

    def test_form_existing_future_periods(self):
        """Tests getting the form for an existing set of ClassPeriods. Also tests
        submitting the form."""
        # Uses a date 3 days into the future.
        date = timezone.now().date() + timedelta(days=3)

        ClassPeriod.objects.bulk_create(
            [
                ClassPeriod(date=date, number=1, max_student_count=10),
                ClassPeriod(date=date, number=2, max_student_count=11),
                ClassPeriod(date=date, number=3, max_student_count=12),
            ]
        )

        # Checks that the form has generated fields according to the value of
        # MAX_PERIOD_NUMBER in the project settings.
        response = self.client.get(
            reverse("future_class_periods_existing", kwargs={"date": str(date)})
        )
        self.assertContains(response, str(date))
        self.assertContains(response, "Period 1")
        self.assertContains(response, "Period 2")
        self.assertContains(response, "Period 3")
        self.assertNotContains(response, "Period 4")

        # Checks that the form's initial values are the existing values in the database.
        self.assertContains(response, "10")
        self.assertContains(response, "11")
        self.assertContains(response, "12")

        # Checks that the form is submitted without any errors.
        response = self.client.post(
            reverse(
                "future_class_periods_existing",
                kwargs={"date": str(date)},
            ),
            {
                "date": str(date + timedelta(days=3)),
                "period_1": "0",
                "period_2": "1",
                "period_3": "2",
            },
        )
        self.assertRedirects(response, reverse("future_class_periods_list"))

        # Checks that the only ClassPeriod objects that exist are the ones created
        # above.
        periods = ClassPeriod.objects.filter(date=date + timedelta(days=3))
        self.assertEqual(periods.count(), 3)

        # Checks that all the ClassPeriods have the correct value for the
        # max_student_count field.
        self.assertEqual(periods[0].max_student_count, 0)
        self.assertEqual(periods[1].max_student_count, 1)
        self.assertEqual(periods[2].max_student_count, 2)
