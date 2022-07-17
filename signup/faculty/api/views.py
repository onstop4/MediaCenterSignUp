from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView

from signup.faculty.api.serializers import ClassPeriodSignUpSerializer
from signup.models import ClassPeriodSignUp


class ClassPeriodSignUpMixin:
    """Contains common logic for the APIViews dealing with :class:`ClassPeriodSignUp`
    objects."""

    queryset = ClassPeriodSignUp.objects.all()
    serializer_class = ClassPeriodSignUpSerializer


class ClassPeriodSignUpListAPIView(ClassPeriodSignUpMixin, ListAPIView):
    filter_backends = [SearchFilter, DjangoFilterBackend]
    filterset_fields = [
        "id",
        "class_period__number",
        "student__name",
        "student__id",
        "date_signed_up",
        "reason",
        "attendance_confirmed",
        "date_attendance_confirmed",
    ]
    search_fields = ["student__name"]


class ClassPeriodSignUpDetailAPIView(
    ClassPeriodSignUpMixin, RetrieveUpdateDestroyAPIView
):
    pass
