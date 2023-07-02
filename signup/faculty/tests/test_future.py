from datetime import timedelta

from constance.test import override_config
from django import forms
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from signup.faculty.forms import FutureClassPeriodsForm
from signup.models import ClassPeriod, ClassPeriodSignUp, LibraryFacultyMember, Student


@override_config(MAX_PERIOD_NUMBER=3)
class TestFutureClassPeriodsForm(TestCase):
    """Performs tests on :class:`signup.faculty.forms.FutureClassPeriodsForm`."""

    def test_form_choices(self):
        """Tests that the choices of the form are generated correctly based on the value
        of ``MAX_PERIOD_NUMBER`` in the Constance settings."""
        form = FutureClassPeriodsForm()
        visible_fields = form.visible_fields()

        # Checks that the integer fields are generated correctly.
        self.assertEqual(visible_fields[0].label, "Period 1")
        self.assertTrue(isinstance(visible_fields[0].field, forms.IntegerField))
        self.assertEqual(visible_fields[1].label, "Period 2")
        self.assertTrue(isinstance(visible_fields[1].field, forms.IntegerField))
        self.assertEqual(visible_fields[2].label, "Period 3")
        self.assertTrue(isinstance(visible_fields[2].field, forms.IntegerField))

        # Checks that the date field and the period fields are the only fields on the
        # form.
        self.assertEqual(len(visible_fields), 3)

    def test_form_validation(self):
        """Tests that the form validates complete and incomplete data correctly."""
        # All data is specified correctly, so everything should be fine.
        form = FutureClassPeriodsForm(
            data={
                "start_date": timezone.now(),
                "period_1": 1,
                "period_2": 0,
                "period_3": 1,
            }
        )
        self.assertTrue(form.is_valid())

        # One or more missing fields should generate an error.
        form = FutureClassPeriodsForm(
            data={"start_date": timezone.now(), "period_1": 1}
        )
        self.assertFalse(form.is_valid())

        # One or more missing fields should generate an error.
        form = FutureClassPeriodsForm(data={})
        self.assertFalse(form.is_valid())

        form = FutureClassPeriodsForm(data={"start_date": timezone.now()})
        self.assertFalse(form.is_valid())

        form = FutureClassPeriodsForm(
            data={"period_1": 1, "period_2": 0, "period_3": 1}
        )
        self.assertFalse(form.is_valid())

        # An integer value lower than zero should generate an error.
        form = FutureClassPeriodsForm(
            data={
                "start_date": timezone.now(),
                "period_1": 1,
                "period_2": 0,
                "period_3": -1,
            }
        )
        self.assertFalse(form.is_valid())


@override_config(MAX_PERIOD_NUMBER=3)
class TestFutureClassPeriodsView(TestCase):
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
        # MAX_PERIOD_NUMBER in the Constance settings.
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
                "start_date": str(date),
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
        # MAX_PERIOD_NUMBER in the Constance settings.
        response = self.client.get(
            reverse("future_class_periods_existing", kwargs={"date": str(date)})
        )
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
                "start_date": str(date),
                "period_1": "20",
                "period_2": "21",
                "period_3": "22",
            },
        )
        self.assertRedirects(response, reverse("future_class_periods_list"))

        # Checks that the only ClassPeriod objects that exist are the ones created
        # above.
        periods = ClassPeriod.objects.filter(date=date)
        self.assertEqual(periods.count(), 3)

        # Checks that all the ClassPeriods have the correct value for the
        # max_student_count field.
        self.assertEqual(periods[0].max_student_count, 20)
        self.assertEqual(periods[1].max_student_count, 21)
        self.assertEqual(periods[2].max_student_count, 22)

    def test_future_periods_with_existing_signups(self):
        """Tests submitting the form when the number of signups exceed the new maximum
        student count for a certain set of periods."""
        # Uses a date 3 days into the future.
        datetime = timezone.now() + timedelta(days=3)
        date = datetime.date()
        student1 = Student.objects.create_user(email="student1@myhchs.org")
        student2 = Student.objects.create_user(email="student2@myhchs.org")

        period1 = ClassPeriod.objects.create(date=date, number=1, max_student_count=2)
        period2 = ClassPeriod.objects.create(date=date, number=2, max_student_count=2)

        # There are now 4 signups, two for each period.
        ClassPeriodSignUp.objects.bulk_create(
            [
                ClassPeriodSignUp(
                    student=student1,
                    class_period=period1,
                    date_signed_up=datetime,
                    reason=ClassPeriodSignUp.STUDY_HALL,
                ),
                ClassPeriodSignUp(
                    student=student2,
                    class_period=period1,
                    date_signed_up=datetime,
                    reason=ClassPeriodSignUp.STUDY_HALL,
                ),
                ClassPeriodSignUp(
                    student=student1,
                    class_period=period2,
                    date_signed_up=datetime,
                    reason=ClassPeriodSignUp.STUDY_HALL,
                ),
                ClassPeriodSignUp(
                    student=student2,
                    class_period=period2,
                    date_signed_up=datetime,
                    reason=ClassPeriodSignUp.STUDY_HALL,
                ),
            ]
        )

        # Attempts to lower the max of the existing periods and create a new period.
        response = self.client.post(
            reverse(
                "future_class_periods_existing",
                kwargs={"date": str(date)},
            ),
            {
                "start_date": str(date),
                "period_1": "1",
                "period_2": "1",
                "period_3": "1",
            },
        )

        # Checks that the form is invalid because the number of signups for the existing
        # periods exceeds the new maximums.
        self.assertContains(
            response,
            f"Period 1 on {date} currently has 2 students, which is greater than the new maximum of 1",
            1,
        )
        self.assertContains(
            response,
            f"Period 2 on {date} currently has 2 students, which is greater than the new maximum of 1",
            1,
        )

        periods = ClassPeriod.objects.values_list("number", "max_student_count")

        # Checks that the existing periods remain the same and the new one has not been
        # created.
        self.assertEqual(periods.count(), 2)
        self.assertTupleEqual(periods[0], (1, 2))
        self.assertTupleEqual(periods[1], (2, 2))

        # Checks that the signups remain the same.
        signups = ClassPeriodSignUp.objects.all()
        self.assertEqual(signups.count(), 4)

        # Deletes one signup from each period, so everything should be fine after this
        # point.
        signups.filter(class_period__number=1).first().delete()
        signups.filter(class_period__number=2).first().delete()

        response = self.client.post(
            reverse(
                "future_class_periods_existing",
                kwargs={"date": str(date)},
            ),
            {
                "start_date": str(date),
                "period_1": "1",
                "period_2": "1",
                "period_3": "1",
            },
        )

        self.assertRedirects(response, reverse("future_class_periods_list"))

        periods = ClassPeriod.objects.values_list("number", "max_student_count")

        # Checks that the new period has been created and the old periods have been
        # updated.
        self.assertEqual(periods.count(), 3)
        self.assertTupleEqual(periods[0], (1, 1))
        self.assertTupleEqual(periods[1], (2, 1))
        self.assertTupleEqual(periods[2], (3, 1))
