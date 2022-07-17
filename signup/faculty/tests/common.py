from django.utils import timezone


def convert_datetime(datetime_obj):
    """Converts datetime object into a form similar to the one used by Django REST
    Framework when it serializes datetime objects."""
    return str(timezone.localtime(datetime_obj)).replace(" ", "T")
