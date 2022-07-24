from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from signup.faculty.tasks import delete_old_periods_and_signups
from signup.models import ClassPeriod, ClassPeriodSignUp, Student


class TestTaskDependencies(TestCase):
    """Tests the functions and methods that tasks in :mod:`signup.faculty.tasks` depend
    on."""

    def test_delete_old_periods_and_signups(self):
        """Tests :func:`signup.faculty.tasks.delete_old_periods_and_signups`. Ensures
        that only ClassPeriods whose date is in the future remain (along with any
        associated ClassPeriodSignUps)."""
        now = timezone.now()
        future = now + timedelta(days=60)

        student = Student.objects.create_user(
            email="student@myhchs.org", password="12345"
        )

        # Creates two ClassPeriods: one for the present and one for the future.
        period1 = ClassPeriod.objects.create(date=now, number=1, max_student_count=10)
        period2 = ClassPeriod.objects.create(
            date=future, number=1, max_student_count=10
        )

        # Creates two ClassPeriodSignUps: one for the present and one for the future.
        ClassPeriodSignUp.objects.create(
            student=student,
            class_period=period1,
            date_signed_up=now,
            reason=ClassPeriodSignUp.STUDY_HALL,
        )
        signup2 = ClassPeriodSignUp.objects.create(
            student=student,
            class_period=period2,
            date_signed_up=future,
            reason=ClassPeriodSignUp.STUDY_HALL,
        )

        delete_old_periods_and_signups()

        # Only the ClassPeriod (and its associated ClassPeriodSignUp) with a date in the
        # future should remain.
        self.assertEqual(ClassPeriod.objects.get(), period2)
        self.assertEqual(ClassPeriodSignUp.objects.get(), signup2)
