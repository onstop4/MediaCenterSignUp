from celery import shared_task
from django.utils import timezone

from signup.models import ClassPeriod


def delete_old_periods_and_signups():
    """Removes ClassPeriods with a date field that is before/equal to today's date. This
    will also cause the deletion of the associated ClassPeriodSignUps."""
    ClassPeriod.objects.get_unordered_queryset().filter(
        date__lte=timezone.now()
    ).delete()


@shared_task(name="Delete Old Signups")
def delete_old_periods_and_signups_task():
    delete_old_periods_and_signups()
