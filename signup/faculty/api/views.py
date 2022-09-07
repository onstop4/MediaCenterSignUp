from tempfile import NamedTemporaryFile

from django.http import HttpResponse
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.permissions import BasePermission
from rest_framework.viewsets import GenericViewSet

from signup.faculty.api.filters import ClassPeriodSignUpFilter, fields
from signup.faculty.api.serializers import ClassPeriodSignUpSerializer
from signup.faculty.api.spreadsheets import generate_spreadsheet
from signup.models import ClassPeriodSignUp, is_library_faculty_member


class IsLibraryFacultyMember(BasePermission):
    def has_permission(self, request, view):
        return is_library_faculty_member(request.user)


class ClassPeriodSignUpViewSet(
    mixins.CreateModelMixin,
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    GenericViewSet,
):
    permission_classes = [IsLibraryFacultyMember]
    queryset = ClassPeriodSignUp.objects.all()
    serializer_class = ClassPeriodSignUpSerializer

    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = ClassPeriodSignUpFilter
    ordering_fields = fields
    search_fields = ["student__name"]
    ordering = ["student__name"]

    @action(detail=False, methods=["GET"])
    def generate_spreadsheet(self, request):
        queryset = self.filter_queryset(self.get_queryset())
        workbook = generate_spreadsheet(queryset)

        # Creates file to temporarily store spreadsheet.
        with NamedTemporaryFile() as temporary_file:
            workbook.save(temporary_file)
            temporary_file.seek(0)
            # Reads file contents as bytes to send back as a response.
            stream = temporary_file.read()

        file_name = timezone.localtime(timezone.now()).strftime("%Y%m%d-%H%M%S")
        return HttpResponse(
            stream,
            headers={
                "Content-Type": "application/vnd.ms-excel",
                "Content-Disposition": f'attachment; filename="{file_name}.xlsx"',
            },
        )
