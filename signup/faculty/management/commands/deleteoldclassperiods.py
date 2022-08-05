from datetime import date

from django.core.management.base import BaseCommand
from django.utils import timezone

from signup.models import ClassPeriod


class Command(BaseCommand):
    """Removes old class periods and signups from previous school years. Accepts two
    arguments: one for the month and one for the day representing the end of the school
    year."""

    help = "Removes old class periods and signups from previous school years."

    def add_arguments(self, parser):
        parser.add_argument("month", type=int, help="Month when this school year ends.")
        parser.add_argument(
            "day", type=int, help="Day of month when this school year ends."
        )

    def handle(self, *args, **options):
        now = timezone.now().date()
        end_of_school_year = date(
            year=now.year, month=options["month"], day=options["day"]
        )

        if end_of_school_year > now:
            end_of_school_year = end_of_school_year.replace(
                year=end_of_school_year.year - 1
            )

        ClassPeriod.objects.filter(date__lte=end_of_school_year).delete()
