from datetime import timedelta

from constance.test import override_config
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from signup.models import ClassPeriod, LibraryFacultyMember


@override_config(MAX_PERIOD_NUMBER=3)
class TestClassPeriodsList(TestCase):
    """Performs tests on :class:`signup.faculty.views.ClassPeriodsListView`."""

    def setUp(self):
        self.library_faculty_member = LibraryFacultyMember.objects.create_user(
            email="faculty@myhchs.org", password="12345"
        )
        self.client.force_login(self.library_faculty_member)

    def create_periods(self):
        """Creates ClassPeriods for today, tomorrow, and yesterday."""
        date = timezone.now()

        # Creates 3 ClassPeriods for today, 3 for tomorrow, and 3 for yesterday.
        ClassPeriod.objects.bulk_create(
            [
                ClassPeriod(date=date, number=1, max_student_count=0),
                ClassPeriod(date=date, number=2, max_student_count=1),
                ClassPeriod(date=date, number=3, max_student_count=2),
                ClassPeriod(
                    date=date + timedelta(days=1), number=1, max_student_count=3
                ),
                ClassPeriod(
                    date=date + timedelta(days=1), number=2, max_student_count=4
                ),
                ClassPeriod(
                    date=date + timedelta(days=1), number=3, max_student_count=5
                ),
                ClassPeriod(
                    date=date - timedelta(days=1), number=1, max_student_count=6
                ),
                ClassPeriod(
                    date=date - timedelta(days=1), number=2, max_student_count=7
                ),
                ClassPeriod(
                    date=date - timedelta(days=1), number=3, max_student_count=8
                ),
            ]
        )

    def test_list_future_periods(self):
        """Tests listing max student counts for class periods today and in the
        future."""
        # Checks that special message is displayed when there are no periods to display.
        response = self.client.get(reverse("future_class_periods_list"))
        self.assertContains(response, "no class periods to display")
        self.assertContains(response, "See past class periods")

        # Checks that the right buttons are displayed.
        self.assertContains(response, "Plan for new day")

        self.create_periods()

        response = self.client.get(reverse("future_class_periods_list"))

        # Checks that the list contains periods of today and in the future. The
        # greater-than sign must be included since the digits 6, 7, or 8 might be used
        # on the page for some purpose other than displaying the max student count.
        self.assertContains(response, ">0", 1)
        self.assertContains(response, ">1", 2)
        self.assertContains(response, ">2", 2)
        self.assertContains(response, ">3", 2)
        self.assertContains(response, ">4", 1)
        self.assertContains(response, ">5", 1)

        # Checks that "Today" appears twice on the page (once in the heading and once to
        # indicate today's set of max student counts).
        self.assertContains(response, "Today", 2)

        # Checks that the list does not contain periods of the past.
        self.assertNotContains(response, ">6")
        self.assertNotContains(response, ">7")
        self.assertNotContains(response, ">8")

    def test_list_past_periods(self):
        """Tests listing max student counts for class periods in the past."""
        # Checks that special message is displayed when there are no periods to display.
        response = self.client.get(reverse("past_class_periods_list"))
        self.assertContains(response, "no class periods to display")

        # Checks that the right buttons are displayed.
        self.assertNotContains(response, "Plan for new day")
        self.assertContains(response, "See class periods today and in the future")

        self.create_periods()

        response = self.client.get(reverse("past_class_periods_list"))

        # Checks that the list contains periods of the past. The greater-than sign must
        # be included since the digits 6, 7, or 8 might be used on the page for some
        # purpose other than displaying the max student count.
        self.assertContains(response, ">6", 1)
        self.assertContains(response, ">7", 1)
        self.assertContains(response, ">8", 1)

        # Checks that the list does not contain periods of today and in the future.
        self.assertNotContains(response, ">0")
        self.assertContains(response, ">1", 1)
        self.assertContains(response, ">2", 1)
        self.assertContains(response, ">3", 1)
        self.assertNotContains(response, ">4")
        self.assertNotContains(response, ">5")

        # Checks that "Today" does not appear on the page, meaning that there is no
        # indicator for todays's set of max student counts.
        self.assertNotContains(response, "Today")
