from django.test import TestCase
from django.utils import timezone

from signup.faculty.spreadsheets import generate_spreadsheet
from signup.models import ClassPeriod, ClassPeriodSignUp, Student, StudentInfo


class CommonTestLogicMixin:
    """Contains common logic for testing spreadsheet-related functionality."""

    def setUp(self):
        # pylint: disable=invalid-name
        student1 = Student.objects.create_user(
            email="student1@myhchs.org", password="12345", name="Student1"
        )
        student2 = Student.objects.create_user(
            email="student2@myhchs.org", password="12345", name="Student2"
        )

        StudentInfo.objects.create(student=student1, id="123456")

        self.now = timezone.localtime(timezone.now())

        first_period = ClassPeriod.objects.create(
            date=self.now, number=1, max_student_count=10
        )
        second_period = ClassPeriod.objects.create(
            date=self.now, number=2, max_student_count=10
        )

        # Creates ClassPeriodSignUp for both students.
        ClassPeriodSignUp.objects.bulk_create(
            [
                ClassPeriodSignUp(
                    student=student1,
                    class_period=first_period,
                    date_signed_up=self.now,
                    reason=ClassPeriodSignUp.LUNCH,
                    attendance_confirmed=True,
                    date_attendance_confirmed=self.now,
                ),
                ClassPeriodSignUp(
                    student=student2,
                    class_period=second_period,
                    date_signed_up=self.now,
                    reason=ClassPeriodSignUp.STUDY_HALL,
                    attendance_confirmed=True,
                    date_attendance_confirmed=self.now,
                ),
            ]
        )


class TestSpreadsheetGeneration(CommonTestLogicMixin, TestCase):
    """Tests :class:`signup.faculty.spreadsheets.generate_spreadsheet`."""

    def test_generate_spreadsheet(self):
        """Tests that the generated spreadsheet contains the correct headings and rows
        for the ClassPeriodSignUps."""
        workbook = generate_spreadsheet(ClassPeriodSignUp.objects.all())

        # Checks that the workbook only contains one sheet.
        self.assertEqual(len(workbook.worksheets), 1)

        sheet = workbook.active

        # Checks that there are only 3 rows: the headings and the two signups.
        rows = list(sheet.rows)
        self.assertEqual(len(rows), 3)

        # Checks that the first row contains the headings.
        first_row_values = [cell.value for cell in rows[0]]
        self.assertEqual(
            first_row_values,
            [
                "Date",
                "Period Number",
                "Student Name",
                "Student ID",
                "Reason",
                "Date Signed Up",
                "Attendance Confirmed",
                "Date Attendance Confirmed",
            ],
        )

        # Checks that the second row contains the first signup.
        second_row_values = [cell.value for cell in rows[1]]
        self.assertEqual(
            second_row_values,
            [
                self.now.date(),
                1,
                "Student1",
                "123456",
                "lunch",
                timezone.localtime(self.now).replace(tzinfo=None),
                True,
                timezone.localtime(self.now).replace(tzinfo=None),
            ],
        )

        # Checks that the third row contains the second signup.
        third_row_values = [cell.value for cell in rows[2]]
        self.assertEqual(
            third_row_values,
            [
                self.now.date(),
                2,
                "Student2",
                None,
                "study hall",
                timezone.localtime(self.now).replace(tzinfo=None),
                True,
                timezone.localtime(self.now).replace(tzinfo=None),
            ],
        )
