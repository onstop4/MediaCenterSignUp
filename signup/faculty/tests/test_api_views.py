from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from signup.faculty.tests.common import convert_datetime
from signup.models import (
    ClassPeriod,
    ClassPeriodSignUp,
    LibraryFacultyMember,
    Student,
    StudentInfo,
)


class CommonTestLogicMixin:
    """Contains common logic for testing views in :mod:`signup.faculty.api.views`."""

    def setUp(self):
        # pylint: disable=invalid-name
        student1 = Student.objects.create_user(
            email="student1@myhchs.org", password="12345", name="Student1"
        )
        StudentInfo.objects.create(student=student1, id="123456")

        student2 = Student.objects.create_user(
            email="student2@myhchs.org", password="12345", name="Student2"
        )
        StudentInfo.objects.create(student=student2, id="654321")

        self.library_faculty_member = LibraryFacultyMember.objects.create_user(
            email="faculty@myhchs.org", password="12345"
        )
        self.client.force_login(self.library_faculty_member)

        self.now = timezone.now()
        period = ClassPeriod.objects.create(
            date=self.now.date(), number=1, max_student_count=10
        )

        # Creates ClassPeriodSignUp for both students.
        self.signup1, self.signup2 = ClassPeriodSignUp.objects.bulk_create(
            [
                ClassPeriodSignUp(
                    id=1,
                    student=student1,
                    class_period=period,
                    date_signed_up=self.now,
                    reason=ClassPeriodSignUp.STUDY_HALL,
                ),
                ClassPeriodSignUp(
                    id=2,
                    student=student2,
                    class_period=period,
                    date_signed_up=self.now,
                    reason=ClassPeriodSignUp.STUDY_HALL,
                ),
            ]
        )


class ClassPeriodSignUpListAPIViewTestCase(CommonTestLogicMixin, APITestCase):
    """Performs tests on :class:`signup.faculty.views.ClassPeriodSignUpListAPIView`."""

    def test_listing_periods_without_filtering(self):
        """Tests listing ClassPeriodSignUps by performing a GET request on
        ``api_periods_list``. Performs no filtering."""
        response = self.client.get(reverse("api_periods_list"))
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.data,
            [
                {
                    "id": self.signup1.id,
                    "period_number": 1,
                    "student_name": "Student1",
                    "student_id": "123456",
                    "date_signed_up": convert_datetime(self.now),
                    "reason": ClassPeriodSignUp.STUDY_HALL,
                    "attendance_confirmed": False,
                    "date_attendance_confirmed": None,
                },
                {
                    "id": self.signup2.id,
                    "period_number": 1,
                    "student_name": "Student2",
                    "student_id": "654321",
                    "date_signed_up": convert_datetime(self.now),
                    "reason": ClassPeriodSignUp.STUDY_HALL,
                    "attendance_confirmed": False,
                    "date_attendance_confirmed": None,
                },
            ],
        )

    def test_listing_periods_with_filtering(self):
        """Tests listing ClassPeriodSignUps by performing a GET request on
        ``api_periods_list`` with url query parameters for filtering."""
        # Tests the DjangoFilterBackend filter backend.
        url = (
            reverse("api_periods_list")
            + f"?id={self.signup2.id}&class_period__number=1&student__name=Student2"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.data,
            [
                {
                    "id": self.signup2.id,
                    "period_number": 1,
                    "student_name": "Student2",
                    "student_id": "654321",
                    "date_signed_up": convert_datetime(self.now),
                    "reason": ClassPeriodSignUp.STUDY_HALL,
                    "attendance_confirmed": False,
                    "date_attendance_confirmed": None,
                }
            ],
        )

        # Tests the SearchFilter filter backend.
        url = reverse("api_periods_list") + "?search=Student2"
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.data,
            [
                {
                    "id": self.signup2.id,
                    "period_number": 1,
                    "student_name": "Student2",
                    "student_id": "654321",
                    "date_signed_up": convert_datetime(self.now),
                    "reason": ClassPeriodSignUp.STUDY_HALL,
                    "attendance_confirmed": False,
                    "date_attendance_confirmed": None,
                }
            ],
        )

        # Tests both filter backends together.
        url = (
            reverse("api_periods_list")
            + f"?id={self.signup2.id}&class_period__number=1&student__name=Student2&search=Student2"
        )
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertListEqual(
            response.data,
            [
                {
                    "id": self.signup2.id,
                    "period_number": 1,
                    "student_name": "Student2",
                    "student_id": "654321",
                    "date_signed_up": convert_datetime(self.now),
                    "reason": ClassPeriodSignUp.STUDY_HALL,
                    "attendance_confirmed": False,
                    "date_attendance_confirmed": None,
                }
            ],
        )


class ClassPeriodSignUpDetailAPIViewTestCase(CommonTestLogicMixin, APITestCase):
    """Performs tests on
    :class:`signup.faculty.views.ClassPeriodSignUpDetailAPIView`."""

    def test_retrieving_period(self):
        """Tests getting info on a single ClassPeriodSignUp by performing a GET request
        on ``api_period``."""
        response = self.client.get(reverse("api_period", kwargs={"pk": "1"}))
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.data,
            {
                "id": self.signup1.id,
                "period_number": 1,
                "student_name": "Student1",
                "student_id": "123456",
                "date_signed_up": convert_datetime(self.now),
                "reason": ClassPeriodSignUp.STUDY_HALL,
                "attendance_confirmed": False,
                "date_attendance_confirmed": None,
            },
        )

    def test_updating_period(self):
        """Tests updating info on a single ClassPeriodSignUp by performing a PATCH
        request on ``api_period``. Also tests that only writable fields are updated."""
        # Attempts to change both a writable field ("attendance_confirmed") and a
        # read-only field ("reason") for the first ClassPeriodSignUp.
        response = self.client.patch(
            reverse("api_period", kwargs={"pk": "1"}),
            {"attendance_confirmed": True, "reason": ClassPeriodSignUp.LUNCH},
        )

        # Checks that the request was valid and that only the writable field of
        # ClassPeriodSignUp ("attendance_confirmed") was modified.
        self.assertEqual(response.status_code, 200)
        self.assertDictEqual(
            response.data,
            {
                "id": self.signup1.id,
                "period_number": 1,
                "student_name": "Student1",
                "student_id": "123456",
                "date_signed_up": convert_datetime(self.now),
                "reason": ClassPeriodSignUp.STUDY_HALL,
                "attendance_confirmed": True,
                "date_attendance_confirmed": None,
            },
        )

    def test_deleting_period(self):
        """Tests deleting a single ClassPeriodSignUp by performing a DELETE request on
        on ``api_period``."""
        # Performs DELETE request.
        response = self.client.delete(reverse("api_period", kwargs={"pk": "1"}))
        self.assertEqual(response.status_code, 204)

        # Checks that the deleted ClassPeriodSignUp no longer exists.
        response = self.client.get(reverse("api_period", kwargs={"pk": "1"}))
        self.assertEqual(response.status_code, 404)
