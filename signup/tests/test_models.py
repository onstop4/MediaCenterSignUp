from django.test import TestCase

from signup.models import LibraryFacultyMember, Student, User


class UserCreationTestCase(TestCase):
    """Tests creating users."""

    def test_create_generic_user(self):
        """Tests that users created from the User model have the correct details,
        including the STUDENT user type."""
        user = User.objects.create_user(email="generic@example.com")
        self.assertEqual(user.user_type, User.STUDENT)

    def test_create_student(self):
        """Tests that users created from the Student model have the correct details,
        including the STUDENT user type."""
        user = Student.objects.create_user(email="student@example.com")
        self.assertEqual(user.user_type, User.STUDENT)

    def test_create_library_faculty_member(self):
        """Tests that users created from the LibraryFacultyMember model have the correct
        details, including the LIBRARY_FACULTY_MEMBER user type."""
        user = LibraryFacultyMember.objects.create_user(email="faculty@example.com")
        self.assertEqual(user.user_type, User.LIBRARY_FACULTY_MEMBER)
