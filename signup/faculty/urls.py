from datetime import datetime

from django.urls import path, register_converter

from signup.faculty.views import ClassPeriodsListView, FutureClassPeriodsFormView


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
        ClassPeriodsListView.as_view(),
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
    path(
        "past/",
        ClassPeriodsListView.as_view(future=False),
        name="past_class_periods_list",
    ),
]
