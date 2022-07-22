from django.test import TestCase
from django.urls import reverse

from signup.models import Student


class TestBasicFacultyViewsAuth(TestCase):
    """Tests that unauthorized users who attempt to access a faculty view (not part of
    the API) are handled correctly."""

    def test_accessing_as_anonymous_user(self):
        """Tests that anonymous users are redirected to the index."""
        response = self.client.get(reverse("future_class_periods_list"))
        self.assertRedirects(response, reverse("index"))

    def test_student(self):
        """Tests that students will get an HTTP 403 error."""
        student = Student.objects.create_user(
            email="student@myhchs.org", password="12345"
        )
        self.client.force_login(student)

        response = self.client.get(reverse("future_class_periods_list"))
        self.assertEqual(response.status_code, 403)
