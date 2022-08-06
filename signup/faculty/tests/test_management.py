from datetime import date, datetime
from unittest.mock import patch

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from signup.models import ClassPeriod, ClassPeriodSignUp, Student


class TestDeleteOldClassPeriods(TestCase):
    """Tests :mod:`signup.faculty.management.commands.deleteoldclassperiods```. Checks
    that the command does not delete ClassPeriods that are part of the current school
    year."""

    def setUp(self):
        student = Student.objects.create_user(
            email="student@myhchs.org", password="12345"
        )

        # Part of the 2021-2022 school year.
        self.period1 = ClassPeriod.objects.create(
            date=date(2022, 4, 1), number=1, max_student_count=10
        )
        # Part of the 2022-2023 school year.
        self.period2 = ClassPeriod.objects.create(
            date=date(2022, 9, 1), number=1, max_student_count=10
        )
        # Part of the 2023-2024 school year.
        self.period3 = ClassPeriod.objects.create(
            date=date(2023, 10, 1), number=1, max_student_count=10
        )

        date_signed_up = timezone.now().replace(year=2022, month=8, day=5)

        self.signup1 = ClassPeriodSignUp.objects.create(
            student=student,
            class_period=self.period1,
            date_signed_up=date_signed_up,
            reason=ClassPeriodSignUp.STUDY_HALL,
        )
        self.signup2 = ClassPeriodSignUp.objects.create(
            student=student,
            class_period=self.period2,
            date_signed_up=date_signed_up,
            reason=ClassPeriodSignUp.STUDY_HALL,
        )
        self.signup3 = ClassPeriodSignUp.objects.create(
            student=student,
            class_period=self.period3,
            date_signed_up=date_signed_up,
            reason=ClassPeriodSignUp.STUDY_HALL,
        )

    def test_delete_old_class_periods_from_last_year(self):
        """Tests deleting ClassPeriods from the previous calendar year that aren't part
        of the current school year."""
        with patch("django.utils.timezone.now") as now_patched:
            # Patches now() function to a time that is part of the 2022-2023 school
            # year.
            now_patched.return_value = datetime(2023, 5, 1)
            # Deletes only self.period1 since it is the only period that is part of the
            # 2021-2022 school year, and the command is not supposed to delete periods
            # that are part of (or after) the current school year.
            call_command("deleteoldclassperiods", 7, 1)

        periods = ClassPeriod.objects.all()
        self.assertQuerysetEqual(periods, [self.period2, self.period3], ordered=False)

        signups = ClassPeriodSignUp.objects.all()
        self.assertQuerysetEqual(signups, [self.signup2, self.signup3], ordered=False)

    def test_delete_old_class_periods_from_last_school_year(self):
        """Tests deleting ClassPeriods from previous school years (including ones that
        are part of the current calendar year."""
        with patch("django.utils.timezone.now") as now_patched:
            # Patches now() function to a time that is part of the 2023-2024 school
            # year.
            now_patched.return_value = datetime(2023, 9, 1)
            # Deletes both self.period1 (which is from year 2022) and self.period2
            # (which is part of the 2022-2023 school year).
            call_command("deleteoldclassperiods", 7, 1)

        periods = ClassPeriod.objects.all()
        self.assertQuerysetEqual(periods, [self.period3])

        signups = ClassPeriodSignUp.objects.all()
        self.assertQuerysetEqual(signups, [self.signup3])
