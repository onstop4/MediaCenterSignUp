from datetime import timedelta

from constance.test import override_config
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from signup.models import ClassPeriod, LibraryFacultyMember


class TestClassPeriodsList(TestCase):
    """Performs tests on :class:`signup.faculty.views.ClassPeriodsListView`."""

    def setUp(self):
        self.library_faculty_member = LibraryFacultyMember.objects.create_user(
            email="faculty@myhchs.org", password="12345"
        )
        self.client.force_login(self.library_faculty_member)

    def create_periods(self):
        """Creates 3 ClassPeriods for today, 3 for tomorrow, and 3 for yesterday."""
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

    @override_config(MAX_PERIOD_NUMBER=3)
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
        self.assertContains(response, ">0</td>", 1)
        self.assertContains(response, ">1</td>", 1)
        self.assertContains(response, ">2</td>", 1)
        self.assertContains(response, ">3</td>", 1)
        self.assertContains(response, ">4</td>", 1)
        self.assertContains(response, ">5</td>", 1)

        # Checks that "Today" appears twice on the page (once in the heading and once to
        # indicate today's set of max student counts).
        self.assertContains(response, "Today", 2)

        # Checks that the list does not contain periods of the past.
        self.assertNotContains(response, ">6</td>")
        self.assertNotContains(response, ">7</td>")
        self.assertNotContains(response, ">8</td>")

    @override_config(MAX_PERIOD_NUMBER=3)
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
        self.assertContains(response, ">6</td>", 1)
        self.assertContains(response, ">7</td>", 1)
        self.assertContains(response, ">8</td>", 1)

        # Checks that the list does not contain periods of today and in the future.
        self.assertNotContains(response, ">0<")
        self.assertNotContains(response, ">1</td>")
        self.assertNotContains(response, ">2</td>")
        self.assertNotContains(response, ">3</td>")
        self.assertNotContains(response, ">4</td>")
        self.assertNotContains(response, ">5</td>")

        # Checks that "Today" does not appear on the page, meaning that there is no
        # indicator for todays's set of max student counts.
        self.assertNotContains(response, "Today")

    def create_period2(self, past=False):
        """Creates 9 ClassPeriods, one for today and 8 for the future. If ``past`` is
        True, then the 9 ClassPeriods will be created for the past instead."""
        date = timezone.now()

        ClassPeriod.objects.bulk_create(
            [
                ClassPeriod(
                    date=date + timedelta(1 * (-1 if past else 1)),
                    number=1,
                    max_student_count=0,
                ),
                ClassPeriod(
                    date=date + timedelta(2 * (-1 if past else 1)),
                    number=1,
                    max_student_count=1,
                ),
                ClassPeriod(
                    date=date + timedelta(3 * (-1 if past else 1)),
                    number=1,
                    max_student_count=2,
                ),
                ClassPeriod(
                    date=date + timedelta(4 * (-1 if past else 1)),
                    number=1,
                    max_student_count=3,
                ),
                ClassPeriod(
                    date=date + timedelta(5 * (-1 if past else 1)),
                    number=1,
                    max_student_count=4,
                ),
                ClassPeriod(
                    date=date + timedelta(6 * (-1 if past else 1)),
                    number=1,
                    max_student_count=5,
                ),
                ClassPeriod(
                    date=date + timedelta(7 * (-1 if past else 1)),
                    number=1,
                    max_student_count=6,
                ),
                ClassPeriod(
                    date=date + timedelta(8 * (-1 if past else 1)),
                    number=1,
                    max_student_count=7,
                ),
                ClassPeriod(
                    date=date + timedelta(9 * (-1 if past else 1)),
                    number=1,
                    max_student_count=8,
                ),
                ClassPeriod(
                    date=date + timedelta(10 * (-1 if past else 1)),
                    number=1,
                    max_student_count=9,
                ),
                ClassPeriod(
                    date=date + timedelta(11 * (-1 if past else 1)),
                    number=1,
                    max_student_count=10,
                ),
                ClassPeriod(
                    date=date + timedelta(12 * (-1 if past else 1)),
                    number=1,
                    max_student_count=11,
                ),
            ]
        )

    @override_config(MAX_PERIOD_NUMBER=1)
    def test_list_future_periods_with_pagination(self):
        """Tests that pagination works correctly when listing max student counts for
        class periods today and in the future."""
        self.create_period2()

        response = self.client.get(reverse("future_class_periods_list"))
        self.assertContains(response, "Page 1 of 2")

        self.assertContains(response, ">0</td>", 1)
        self.assertContains(response, ">1</td>", 1)
        self.assertContains(response, ">2</td>", 1)
        self.assertContains(response, ">3</td>", 1)
        self.assertContains(response, ">4</td>", 1)
        self.assertContains(response, ">5</td>", 1)
        self.assertContains(response, ">6</td>", 1)
        self.assertContains(response, ">7</td>", 1)
        self.assertContains(response, ">8</td>", 1)
        self.assertContains(response, ">9</td>", 1)
        self.assertNotContains(response, ">10</td>")
        self.assertNotContains(response, ">11</td>")

        response = self.client.get(reverse("future_class_periods_list") + "?page=2")
        self.assertContains(response, "Page 2 of 2")
        self.assertContains(response, ">10<", 1)
        self.assertContains(response, ">11<", 1)

    @override_config(MAX_PERIOD_NUMBER=1)
    def test_list_past_periods_with_pagination(self):
        """Tests that pagination works correctly when listing max student counts for
        class periods in the past."""
        self.create_period2(True)

        response = self.client.get(reverse("past_class_periods_list"))
        self.assertContains(response, "Page 1 of 2")

        self.assertContains(response, ">0</td>", 1)
        self.assertContains(response, ">1</td>", 1)
        self.assertContains(response, ">2</td>", 1)
        self.assertContains(response, ">3</td>", 1)
        self.assertContains(response, ">4</td>", 1)
        self.assertContains(response, ">5</td>", 1)
        self.assertContains(response, ">6</td>", 1)
        self.assertContains(response, ">7</td>", 1)
        self.assertContains(response, ">8</td>", 1)
        self.assertContains(response, ">9</td>", 1)
        self.assertNotContains(response, ">10</td>")
        self.assertNotContains(response, ">11</td>")

        response = self.client.get(reverse("past_class_periods_list") + "?page=2")
        self.assertContains(response, "Page 2 of 2")
        self.assertContains(response, ">10<", 1)
        self.assertContains(response, ">11<", 1)
