from django.contrib.auth import authenticate
from django.test import RequestFactory, TestCase

from signup.auth import OAuthBackend, UserDetails
from signup.models import LibraryFacultyMember, Student, User


class TestUserCreation(TestCase):
    """Tests creating users."""

    def test_create_generic_user(self):
        """Tests that users created from the User model have the correct details,
        including the STUDENT user type."""
        user = User.objects.create_user(email="generic@myhchs.org")
        self.assertEqual(user.user_type, User.STUDENT)

    def test_create_student(self):
        """Tests that users created from the Student model have the correct details,
        including the STUDENT user type."""
        user = Student.objects.create_user(email="student@myhchs.org")
        self.assertEqual(user.user_type, User.STUDENT)

    def test_create_library_faculty_member(self):
        """Tests that users created from the LibraryFacultyMember model have the correct
        details, including the LIBRARY_FACULTY_MEMBER user type."""
        user = LibraryFacultyMember.objects.create_user(email="faculty@myhchs.org")
        self.assertEqual(user.user_type, User.LIBRARY_FACULTY_MEMBER)


class TestOAuthBackend(TestCase):
    """Tests :class:`signup.auth.OAuthBackend`."""

    def setUp(self):
        self.backend = OAuthBackend()
        self.factory = RequestFactory()
        self.existing_user = User.objects.create_user(email="generic@myhchs.org")

    def test_authenticate_method(self):
        """Tests the backend's :meth:`authenticate` method."""
        request = self.factory.get("/")
        # Asserts that there is only one existing user.
        self.assertEqual(User.objects.count(), 1)

        # Checks that the backend will reject clients (new and existing) whose email
        # address doesn't end with "@myhchs.org".
        none = self.backend.authenticate(
            request, UserDetails("student@example.com", "Student")
        )
        self.assertIsNone(none)
        self.assertEqual(User.objects.count(), 1)

        # Checks that new users will be registered if their email address ends with
        # "@myhchs.org".
        new_user = self.backend.authenticate(
            request, UserDetails("student@myhchs.org", "ActualStudent")
        )
        self.assertIsNotNone(new_user)
        self.assertEqual(User.objects.count(), 2)

        # Checks that existing users will be returned if their email address ends with
        # "@myhchs.org".
        existing_user = self.backend.authenticate(
            request, UserDetails(self.existing_user.email, self.existing_user.name)
        )
        self.assertEqual(existing_user, self.existing_user)
        self.assertEqual(User.objects.count(), 2)

    def test_get_user(self):
        """Tests the backend's :meth:`get_user` method."""
        # Checks that an existing user will be found.
        existing_user = self.backend.get_user(self.existing_user.pk)
        self.assertEqual(existing_user, self.existing_user)

        # Checks that a non-existant user will not found.
        none = self.backend.get_user(2)
        self.assertIsNone(none)

    def test_user_can_authenticate(self):
        """Tests the backend's :meth:`can_authenticate` method."""
        # Checks that the existing user is recognized as active, which is the default
        # state.
        self.assertTrue(self.existing_user)
        # Checks that an inactive user is recognized by the backend as inactive.
        self.assertFalse(
            User.objects.create_user(
                email="inactive@myhchs.org", password="12345", is_active=False
            ).is_active
        )

    def test_multiple_backends(self):
        """Tests that the backend does not interfere with other authentication backends
        like Django's :class:`ModelBackend`."""
        request = self.factory.get("/")
        user = User.objects.create_user(email="user@myhchs.org", password="12345")
        found_user = authenticate(request, email="user@myhchs.org", password="12345")
        self.assertEqual(user, found_user)

    def test_uppercase_email_address(self):
        """Tests that the backend accepts email addresses that end with "@myhchs.org",
        "@MYHCHS.ORG", or some variation of the two."""
        request = self.factory.get("/")
        new_user = self.backend.authenticate(
            request, UserDetails("student@MYHCHS.org", "Student")
        )
        self.assertIsNotNone(new_user)
        self.assertEqual(User.objects.count(), 2)
