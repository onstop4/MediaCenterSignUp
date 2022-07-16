from django.test import TestCase
from django.utils import timezone

from signup.faculty.serializers import ClassPeriodSignUpSerializer
from signup.models import ClassPeriod, ClassPeriodSignUp, Student, StudentInfo


def convert_datetime(datetime_obj):
    """Converts datetime object into a form similar to the one used by Django REST
    Framework when it serializes datetime objects."""
    return str(timezone.localtime(datetime_obj)).replace(" ", "T")


class ClassPeriodSignUpSerializerTestCase(TestCase):
    """Performs tests on
    :class:`signup.faculty.serializers.ClassPeriodSignUpSerializer`."""

    def setUp(self):
        student1 = Student.objects.create_user(
            email="student1@myhchs.org", password="12345", name="Student1"
        )
        StudentInfo.objects.create(student=student1, id="123456")

        student2 = Student.objects.create_user(
            email="student2@myhchs.org", password="12345", name="Student2"
        )
        StudentInfo.objects.create(student=student2, id="654321")

        self.now = timezone.now()
        period = ClassPeriod.objects.create(
            date=self.now.date(), number=1, max_student_count=10
        )

        # Creates ClassPeriodSignUp for both students.
        self.signup1, self.signup2 = ClassPeriodSignUp.objects.bulk_create(
            [
                ClassPeriodSignUp(
                    student=student1,
                    class_period=period,
                    date_signed_up=self.now,
                    reason=ClassPeriodSignUp.STUDY_HALL,
                ),
                ClassPeriodSignUp(
                    student=student2,
                    class_period=period,
                    date_signed_up=self.now,
                    reason=ClassPeriodSignUp.STUDY_HALL,
                ),
            ]
        )

    def test_serialize_single(self):
        """Tests serializing the signups created in setUp() individually."""
        serializer = ClassPeriodSignUpSerializer(self.signup1)
        # Checks that the serializer's data matches the expected data.
        self.assertDictEqual(
            serializer.data,
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

        serializer = ClassPeriodSignUpSerializer(self.signup2)
        # Checks that the serializer's data matches the expected data.
        self.assertDictEqual(
            serializer.data,
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
        )

    def test_serialize_many(self):
        """Tests serializing both signups creates in setUp() together."""
        serializer = ClassPeriodSignUpSerializer(
            [self.signup1, self.signup2], many=True
        )

        # Checks that the serializer's data includes both signups.
        self.assertListEqual(
            serializer.data,
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

    def test_modify_fields(self):
        """Tests how the serializer handles incoming data. Ensures that data that
        attempts to modify read-only fields are rejected."""
        serializer = ClassPeriodSignUpSerializer(
            self.signup1,
            data={
                "student_id": "000000",
                "reason": ClassPeriodSignUp.LUNCH,
                "attendance_confirmed": True,
            },
            partial=True,
        )

        # Checks that the data is valid.
        self.assertTrue(serializer.is_valid())

        # Checks that the only field that was modified was the "attendance_confirmed"
        # field.
        self.assertDictEqual(
            serializer.validated_data,
            {
                "attendance_confirmed": True,
            },
        )
