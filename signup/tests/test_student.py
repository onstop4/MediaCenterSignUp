from datetime import datetime, time
from unittest.mock import patch

from constance.test import override_config
from django import forms
from django.db.utils import IntegrityError
from django.test import TestCase, TransactionTestCase
from django.urls import reverse
from django.utils import timezone

from signup.forms import StudentInfoForm, StudentSignUpForm
from signup.models import (
    ClassPeriod,
    ClassPeriodSignUp,
    LibraryFacultyMember,
    Student,
    StudentInfo,
    student_has_info,
)


class TestBasicStudentViewsAuth(TestCase):
    """Tests that users who are not students are redirected properly."""

    def test_accessing_as_anonymous_user(self):
        """Tests that anonymous users are redirected to the index."""
        response = self.client.get(reverse("student_info_form"))
        self.assertRedirects(response, reverse("index"))

        response = self.client.post(reverse("student_info_form"), {"id": "123456"})
        self.assertRedirects(response, reverse("index"))

    def test_accessing_as_library_faculty_member(self):
        """Tests that library faculty members are redirected to one of their views."""
        library_faculty_member = LibraryFacultyMember.objects.create_user(
            email="faculty@myhchs.org", password="12345"
        )
        self.client.force_login(library_faculty_member)

        response = self.client.get(reverse("student_info_form"), follow=True)
        self.assertRedirects(response, reverse("future_class_periods_list"))


class TestStudentInfoForm(TransactionTestCase):
    """Performs tests on :class:`signup.forms.StudentInfoForm`."""

    def test_student_id_validation(self):
        """Tests that the form validates data correctly."""
        form = StudentInfoForm(data={"id": "123456"})
        self.assertTrue(form.is_valid())

        form = StudentInfoForm(data={"id": "1234567"})
        self.assertFalse(form.is_valid())

        form = StudentInfoForm(data={"id": "1234a6"})
        self.assertFalse(form.is_valid())

        form = StudentInfoForm(data={"id": "12੩456"})
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


class TestStudentInfoView(TestCase):
    """Tests functionality that involves handling student info. This
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


@override_config(
    LUNCH_PERIODS_START=5, LUNCH_PERIODS_END=7, FORCE_OPEN_SIGN_UP_FORM=True
)
class TestStudentSignUpForm(TestCase):
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

    def test_student_already_signed_up_for_period(self):
        """Tests that the form does not list periods that the logged-in student has
        already signed up for. Also tests that said student cannot sign up for a period
        that they already signed up for."""
        student = Student.objects.create(email="student@myhchs.org", password="12345")

        # Tests that first period is still listed.
        form = StudentSignUpForm(student=student)
        self.assertEqual(form.visible_fields()[0].label, "Period 1")

        # Student signs up for first period.
        ClassPeriodSignUp.objects.create(
            student=student,
            class_period=self.first_period,
            reason=ClassPeriodSignUp.STUDY_HALL,
        )

        # First period is no longer listed on the form.
        form = StudentSignUpForm(student=student)
        self.assertEqual(form.visible_fields()[0].label, "Period 3")


@override_config(
    LUNCH_PERIODS_START=5, LUNCH_PERIODS_END=7, FORCE_OPEN_SIGN_UP_FORM=True
)
class TestStudentSignUpView(TestCase):
    """Performs tests on :class:`signup.views.StudentSignUpFormView`. This includes
    testing that the form is rendered correctly, that form submissions are processed
    correctly, and that the form opens and closes correctly."""

    def setUp(self):
        self.student1 = Student.objects.create_user(
            email="student1@myhchs.org", password="12345"
        )
        StudentInfo.objects.create(student=self.student1, id="123456")
        self.client.force_login(self.student1)

        self.student2 = Student.objects.create_user(
            email="student2@myhchs.org", password="12345"
        )
        StudentInfo.objects.create(student=self.student2, id="654321")

        self.now = timezone.now()
        ClassPeriod.objects.create(date=self.now, number=1, max_student_count=1)

    def add_period_6(self):
        """Adds a lunch period to the form. This lunch period has a max student count of
        2."""
        # Max student count is 2 so that I can sign up as both student1 and student2.
        ClassPeriod.objects.create(date=self.now, number=6, max_student_count=2)

    def switch_to_student2(self):
        """Logs `self.client` in as student2."""
        self.client.force_login(self.student2)

    def test_form_submission_then_capacity_reached(self):
        """Tests that once a period's capacity is reached, students can no longer sign
        up for that period."""
        response = self.client.get(reverse("student_sign_up_form"))
        self.assertContains(response, "Period 1")

        response = self.client.post(reverse("student_sign_up_form"), {"period_1": True})
        self.assertRedirects(response, reverse("student_sign_up_success"))

        self.assertEqual(ClassPeriodSignUp.objects.count(), 1)
        response = self.client.get(reverse("student_sign_up_form"))
        self.assertNotContains(response, "Period 1")

    def test_choices(self):
        """Tests that the "lunch" and "study hall" choices are only listed when there is
        a lunch period on the form."""
        # Lunch period is not on form, so "lunch" and "study hall" shouldn't be on form.
        response = self.client.get(reverse("student_sign_up_form"))
        self.assertNotContains(response, "Period 6")
        # Makes all letters lowercase for consistency.
        content = str(response.content).lower()
        self.assertFalse("lunch" in content or "study hall" in content)

        self.add_period_6()

        # Lunch period is on form, so "lunch" and "study hall" should be on form.
        response = self.client.get(reverse("student_sign_up_form"))
        self.assertContains(response, "Period 6")
        content = str(response.content).lower()
        self.assertTrue("lunch" in content or "study hall" in content)

    def test_form_submission_lunch_or_study_hall(self):
        """Tests that the only accepted values for a lunch period field are "L" or "S"."""
        self.add_period_6()

        # Checks that "Q" is not accepted for a lunch period.
        response = self.client.post(reverse("student_sign_up_form"), {"period_6": "Q"})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "error")

        # Checks that "L" is accepted for a lunch period.
        response = self.client.post(reverse("student_sign_up_form"), {"period_6": "L"})
        self.assertRedirects(response, reverse("student_sign_up_success"))

        self.switch_to_student2()

        # Checks that lunch period is still part of form.
        response = self.client.get(reverse("student_sign_up_form"))
        self.assertContains(response, "Period 6")

        # Checks that "S" is accepted for a lunch period.
        response = self.client.post(reverse("student_sign_up_form"), {"period_6": "S"})
        self.assertRedirects(response, reverse("student_sign_up_success"))

        # Checks that both form responses were accepted.
        response = self.client.get(reverse("student_sign_up_form"))
        self.assertNotContains(response, "Period 6")

    def test_student_already_signed_up_for_period(self):
        """Tests that the form does not list periods that the logged-in student has
        already signed up for. Also tests that said student cannot sign up for a period
        that they already signed up for."""
        self.add_period_6()

        # Signing up for lunch period as student1.
        response = self.client.post(reverse("student_sign_up_form"), {"period_6": "L"})
        self.assertRedirects(response, reverse("student_sign_up_success"))

        # Form does not contain lunch period for student1.
        response = self.client.get(reverse("student_sign_up_form"))
        self.assertNotContains(response, "Period 6")

        self.switch_to_student2()

        # Form contains lunch period for student2.
        response = self.client.get(reverse("student_sign_up_form"))
        self.assertContains(response, "Period 6")

        # Signing up for lunch period as student2.
        response = self.client.post(reverse("student_sign_up_form"), {"period_6": "L"})
        self.assertRedirects(response, reverse("student_sign_up_success"))

        # Form does not contain lunch period for student2.
        response = self.client.get(reverse("student_sign_up_form"))
        self.assertNotContains(response, "Period 6")

    def test_open_close_form(self):
        """Tests that the form opens and closes on time. Also tests that the
        ``FORCE_OPEN_SIGN_UP_FORM`` value in the Constance settings also works
        correctly."""
        time_opens = time(6)
        time_closes = time(10)

        with patch("django.utils.timezone.localtime") as localtime_patched:
            # Patches localtime() function to 12:00 PM, which is after the closing time
            # specified above (which is 10:00 AM).
            localtime_patched.return_value = datetime(2022, 1, 1, 12)

            # Forces form to be open.
            with override_config(
                SIGN_UP_FORM_OPENS_TIME=time_opens, SIGN_UP_FORM_CLOSES_TIME=time_closes
            ):
                response = self.client.get(reverse("student_sign_up_form"))
                self.assertContains(response, "Period 1")

            # Doesn't force form to be open so it should be closed.
            with override_config(
                SIGN_UP_FORM_OPENS_TIME=time_opens,
                SIGN_UP_FORM_CLOSES_TIME=time_closes,
                FORCE_OPEN_SIGN_UP_FORM=False,
            ):
                response = self.client.get(reverse("student_sign_up_form"))
                self.assertContains(response, "Closed")


@override_config(FORCE_OPEN_SIGN_UP_FORM=True)
class TestStudentSignUpSuccessView(TestCase):
    """Performs tests on :class:`signup.forms.StudentSignUpSuccessView`. This includes
    testing that it lists all the periods that the student signed up for today."""

    def setUp(self):
        student = Student.objects.create(email="student@myhchs.org", password="12345")
        StudentInfo.objects.create(student=student, id="123456")
        self.client.force_login(student)

        now = timezone.now()
        ClassPeriod.objects.bulk_create(
            [
                ClassPeriod(date=now, number=1, max_student_count=1),
                ClassPeriod(date=now, number=2, max_student_count=1),
            ]
        )

    def test_without_submission(self):
        """Tests that no periods are listed when the student hasn't signed up for any."""
        response = self.client.get(reverse("student_sign_up_success"))
        self.assertContains(response, "Media Center.")
        self.assertNotContains(response, "Period")

    def test_with_submission(self):
        """Tests that all of the periods that the student signed up for are listed."""
        # Checks what happens when the student only signs up for one period.
        response = self.client.post(
            reverse("student_sign_up_form"), {"period_1": True}, follow=True
        )
        self.assertRedirects(response, reverse("student_sign_up_success"))
        self.assertContains(response, "following class periods:")
        self.assertContains(response, "Period 1")
        self.assertNotContains(response, "Period 2")

        # Checks what happens when the student has signed up for two periods in total.
        response = self.client.post(
            reverse("student_sign_up_form"), {"period_2": True}, follow=True
        )
        self.assertRedirects(response, reverse("student_sign_up_success"))
        self.assertContains(response, "following class periods:")
        self.assertContains(response, "Period 1")
        self.assertContains(response, "Period 2")

        # Checks that all the periods that the student signed up for are listed on the
        # page.
        response = self.client.get(reverse("student_sign_up_success"))
        self.assertContains(response, "following class periods:")
        self.assertContains(response, "Period 1")
        self.assertContains(response, "Period 2")
