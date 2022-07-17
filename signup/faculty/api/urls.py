from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from signup.faculty.api.views import (
    ClassPeriodSignUpDetailAPIView,
    ClassPeriodSignUpListAPIView,
)

urlpatterns = [
    path("periods/", ClassPeriodSignUpListAPIView.as_view(), name="api_periods_list"),
    path(
        "periods/<int:pk>/", ClassPeriodSignUpDetailAPIView.as_view(), name="api_period"
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)
