from django.db.utils import IntegrityError
from django.test import Client, TestCase, TransactionTestCase
from django.urls import reverse

from signup.forms import StudentInfoForm
from signup.models import Student, StudentInfo, student_has_info


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
