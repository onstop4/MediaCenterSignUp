from django import forms
from django.db.utils import IntegrityError
from django.test import Client, TestCase, TransactionTestCase, override_settings
from django.urls import reverse
from django.utils import timezone

from signup.forms import StudentInfoForm, StudentSignUpForm
from signup.models import (
    ClassPeriod,
    ClassPeriodSignUp,
    Student,
    StudentInfo,
    student_has_info,
)


class StudentInfoFormTestCase(TransactionTestCase):
    """Performs tests on :class:`signup.forms.StudentInfoForm`."""

    def test_student_id_validation(self):
        """Tests that the form validates data correctly."""
        form = StudentInfoForm(data={"id": "123456"})
        self.assertTrue(form.is_valid())

        form = StudentInfoForm(data={"id": "1234567"})
        self.assertFalse(form.is_valid())

        form = StudentInfoForm(data={"id": "1234a6"})
        self.assertFalse(form.is_valid())

    def test_saving_form(self):
        """Tests that the form can only be saved when a student is specified."""
        # Student is not speciified, so saving the form should lead to an
        # IntegrityError.
        form = StudentInfoForm(data={"id": "123456"})
        with self.assertRaises(IntegrityError):
            form.save()

        # Student is specified, so there should be no problem saving the form.
        student = Student.objects.create(email="student@myhchs.org", password="12345")
        form.instance.student = student
        form.save()
        self.assertEqual(student.info.id, "123456")


class StudentInfoViewTestCase(TestCase):
    """Tests that the functionality related to student info is handled correctly. This
    includes:
    * Testing that students who haven't filled out the student info form must fill it
    out.
    * Testing that the form validates data correctly.
    * Testing that the form cannot be filled out again.
    """

    # pylint: disable=no-member

    def setUp(self):
        self.student = Student.objects.create_user(
            email="student@myhchs.org", password="12345"
        )
        self.client.force_login(self.student)

    def test_anonymous_user(self):
        """Tests that anonymous users are redirected to the index."""
        anonymous_client = Client()

        response = anonymous_client.get(reverse("student_info_form"))
        self.assertRedirects(response, reverse("index"))

        response = anonymous_client.post(reverse("student_info_form"), {"id": "123456"})
        self.assertRedirects(response, reverse("index"))

    def test_new_student_info(self):
        """Tests that new students are required to fill out student info form. Also
        tests that said form functions correctly."""
        # Checks that new students must fill out form.
        response = self.client.get(reverse("student_sign_up_form"))
        self.assertRedirects(response, reverse("student_info_form"))

        # Checks that form processes data correctly.
        response = self.client.post(reverse("student_info_form"), {"id": "123456"})
        self.assertRedirects(response, reverse("student_sign_up_form"))
        self.assertEqual(self.student.info.id, "123456")

    def test_student_id_validation(self):
        """Tests that form validation works correctly."""
        # pylint: disable=pointless-statement

        response = self.client.post(reverse("student_info_form"), {"id": "1234567"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")

        response = self.client.post(reverse("student_info_form"), {"id": "1234a6"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")

        response = self.client.post(reverse("student_info_form"), {"id": ""})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")

        # Checks that all of the form submissions were rejected and that StudentInfo
        # still does not exist for self.student.
        with self.assertRaises(StudentInfo.DoesNotExist):
            self.student.info

    def test_existing_student_info(self):
        """Tests that a student cannot access or fill out the form again."""

        StudentInfo.objects.create(student=self.student, id="123456")

        # Checks that GET requests get redirected to the student sign-up form.
        response = self.client.get(reverse("student_info_form"))
        self.assertRedirects(response, reverse("student_sign_up_form"))

        # Checks that POST requests get redirected to the student sign-up form and that
        # no data is processed.
        response = self.client.post(reverse("student_info_form"), {"id": "654321"})
        self.assertRedirects(response, reverse("student_sign_up_form"))
        self.assertEqual(self.student.info.id, "123456")

    def test_student_has_info_function(self):
        """Tests that :class:`signup.models.student_has_info` works correctly."""
        self.assertFalse(student_has_info(self.student))

        StudentInfo.objects.create(student=self.student, id="123456")
        self.assertTrue(student_has_info(self.student))


@override_settings(LUNCH_PERIODS_START=5)
@override_settings(LUNCH_PERIODS_END=7)
class StudentSignUpFormTestCase(TestCase):
    """Performs tests on :class:`signup.forms.StudentSignUpForm`."""

    def setUp(self):
        now = timezone.now()
        self.first_period = ClassPeriod(date=now, number=1, max_student_count=1)
        ClassPeriod.objects.bulk_create(
            [
                self.first_period,
                ClassPeriod(date=now, number=2, max_student_count=0),
                ClassPeriod(date=now, number=3, max_student_count=1),
                ClassPeriod(date=now, number=4, max_student_count=0),
                ClassPeriod(date=now, number=5, max_student_count=1),
                ClassPeriod(date=now, number=6, max_student_count=0),
                ClassPeriod(date=now, number=7, max_student_count=1),
                ClassPeriod(date=now, number=8, max_student_count=0),
                ClassPeriod(date=now, number=9, max_student_count=1),
            ]
        )

    def test_form_choices_for_lunch_or_study_hall(self):
        """Tests that students are able to indicate that they are signing up for lunch
        or for study hall for periods between `LUNCH_PERIODS_START` and
        `LUNCH_PERIODS_END`. For the other periods, students can only indicate that they
        are signing up because they have study hall."""
        form = StudentSignUpForm()
        visible_fields = form.visible_fields()

        self.assertEqual(visible_fields[0].label, "Period 1")
        self.assertTrue(isinstance(visible_fields[0].field, forms.BooleanField))

        self.assertEqual(visible_fields[1].label, "Period 3")
        self.assertTrue(isinstance(visible_fields[1].field, forms.BooleanField))

        self.assertEqual(visible_fields[2].label, "Period 5")
        self.assertTrue(isinstance(visible_fields[2].field, forms.ChoiceField))

        self.assertEqual(visible_fields[3].label, "Period 7")
        self.assertTrue(isinstance(visible_fields[3].field, forms.ChoiceField))

        self.assertEqual(visible_fields[4].label, "Period 9")
        self.assertTrue(isinstance(visible_fields[4].field, forms.BooleanField))

    def test_form_choices_for_max_capacity(self):
        """Tests that a period will not be listed on the form if it has reached
        capacity."""
        # Period 1 hasn't reached capacity yet, so it should still be on the form.
        form = StudentSignUpForm()
        visible_fields = form.visible_fields()
        self.assertEqual(visible_fields[0].label, "Period 1")

        student = Student.objects.create_user(
            email="student@myhchs.org", password="12345"
        )

        # Period 1 has now reached capacity.
        ClassPeriodSignUp.objects.create(
            student=student, class_period=self.first_period
        )

        # Period 1 shouldn't be on the form now.
        form = StudentSignUpForm()
        visible_fields = form.visible_fields()
        self.assertEqual(visible_fields[0].label, "Period 3")

    def test_form_validation_of_field_keys(self):
        """Tests that no parts of the form are required. Also tests that the form
        ignores nonexistant fields."""

        # Only one field filled out.
        form = StudentSignUpForm(data={"period_1": True})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["period_1"], True)

        # No fields filled out.
        form = StudentSignUpForm(data={})
        self.assertTrue(form.is_valid())

        # Nonexistant field filled out.
        form = StudentSignUpForm(data={"period_100": True})
        self.assertTrue(form.is_valid())
        self.assertIsNone(form.cleaned_data.get("period_100"))

    def test_form_validation_of_field_values(self):
        """Tests that the form correctly interprets the values of the fields."""
        # "L" is a valid choice for a lunch+study period.
        form = StudentSignUpForm(data={"period_5": "L"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["period_5"], "L")

        # "S" is a valid choice for a lunch+study period.
        form = StudentSignUpForm(data={"period_7": "S"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["period_7"], "S")

        # "L" is interpreted as True for a study-only period.
        form = StudentSignUpForm(data={"period_1": "L"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["period_1"], True)

        # "Q" is not a valid choice for a lunch+study period. Only "L", "S", and "" are
        # valid choices.
        form = StudentSignUpForm(data={"period_7": "Q"})
        self.assertFalse(form.is_valid())

        # True is not a valid choice for a lunch+study period. Only "L", "S", and "" are
        # valid choices.
        form = StudentSignUpForm(data={"period_7": True})
        self.assertFalse(form.is_valid())

        # An empty string is falsy.
        form = StudentSignUpForm(data={"period_7": ""})
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data["period_7"])

        # "Q" is a valid choice for a study-only period because that BooleanFields are
        # only concerned with whether a value is truthy or falsy.
        form = StudentSignUpForm(data={"period_1": "Q"})
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data["period_1"], True)

        # An empty string is falsy.
        form = StudentSignUpForm(data={"period_1": ""})
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data["period_1"])
