from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import BasePermission

from signup.faculty.api.serializers import ClassPeriodSignUpSerializer
from signup.models import ClassPeriodSignUp, is_library_faculty_member


class IsLibraryFacultyMember(BasePermission):
    def has_permission(self, request, view):
        return is_library_faculty_member(request.user)


class ClassPeriodSignUpMixin:
    """Contains common logic for the APIViews dealing with :class:`ClassPeriodSignUp`
    objects."""

    permission_classes = [IsLibraryFacultyMember]
    queryset = ClassPeriodSignUp.objects.all()
    serializer_class = ClassPeriodSignUpSerializer


class ClassPeriodSignUpListAPIView(ClassPeriodSignUpMixin, ListAPIView):
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_fields = ordering_fields = [
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
    ordering = ["student__name"]


class ClassPeriodSignUpDetailAPIView(
    ClassPeriodSignUpMixin, RetrieveUpdateDestroyAPIView
):
    pass
