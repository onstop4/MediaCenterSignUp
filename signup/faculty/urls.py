from datetime import datetime

from django.urls import path, register_converter

from signup.faculty.views import FutureClassPeriodsFormView, FutureClassPeriodsListView


# Adapted from https://stackoverflow.com/a/61134265.
class DateConverter:
    """Converts dates to/from URL arguments."""

    regex = r"\d{4}-\d{2}-\d{2}"

    def to_python(self, value):
        return datetime.strptime(value, "%Y-%m-%d").date()

    def to_url(self, value):
        return str(value)


register_converter(DateConverter, "date")

urlpatterns = [
    path(
        "future/",
        FutureClassPeriodsListView.as_view(),
        name="future_class_periods_list",
    ),
    path(
        "future/new/",
        FutureClassPeriodsFormView.as_view(),
        name="future_class_periods_new",
    ),
    path(
        "future/<date>/",
        FutureClassPeriodsFormView.as_view(),
        name="future_class_periods_existing",
    ),
]
