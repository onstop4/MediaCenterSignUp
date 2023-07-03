from datetime import datetime

from django.urls import include, path, register_converter

from signup.faculty.views import (
    ClassPeriodsListView,
    FutureClassPeriodsFormView,
    IndexRedirectView,
    SettingsFormView,
    SignUpsView,
)


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
    path("", IndexRedirectView.as_view(), name="faculty_index"),
    path(
        "periods/",
        ClassPeriodsListView.as_view(),
        name="future_class_periods_list",
    ),
    path(
        "periods/new/",
        FutureClassPeriodsFormView.as_view(),
        name="future_class_periods_new",
    ),
    path(
        "periods/<start_date>/",
        FutureClassPeriodsFormView.as_view(),
        name="future_class_periods_existing",
    ),
    path(
        "past/",
        ClassPeriodsListView.as_view(future=False),
        name="past_class_periods_list",
    ),
    path("signups/", SignUpsView.as_view(), name="signups_app"),
    path("settings/", SettingsFormView.as_view(), name="settings_form"),
    # API urls.
    path("api/", include("signup.faculty.api.urls")),
]
