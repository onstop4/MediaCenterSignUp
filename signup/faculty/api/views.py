from tempfile import NamedTemporaryFile

from django.core.mail import send_mail, send_mass_mail
from django.http import HttpResponse
from django.utils import timezone
from django.utils.formats import date_format
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import OrderingFilter, SearchFilter
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from signup.faculty.api.filters import ClassPeriodSignUpFilter, fields
from signup.faculty.api.serializers import ClassPeriodSignUpSerializer
from signup.faculty.api.spreadsheets import generate_spreadsheet
from signup.models import ClassPeriodSignUp, is_library_faculty_member

DATE_FORMAT = "F j, Y"


class IsLibraryFacultyMember(BasePermission):
    def has_permission(self, request, view):
        return is_library_faculty_member(request.user)


class ClassPeriodSignUpViewSet(ModelViewSet):
    permission_classes = [IsLibraryFacultyMember]
    queryset = ClassPeriodSignUp.objects.all()
    serializer_class = ClassPeriodSignUpSerializer

    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    filterset_class = ClassPeriodSignUpFilter
    ordering_fields = fields
    search_fields = ["student__name"]
    ordering = ["student__name"]

    def destroy(self, request, *args, **kwargs):
        signup = self.get_object()
        period = signup.class_period

        if period.date >= timezone.localdate(timezone.now()):
            period_date_formatted = date_format(period.date, DATE_FORMAT)
            send_mail(
                "Media Center Sign-Up Removal",
                f"You signed up to use the Holy Cross Media Center during period {period.number} on {period_date_formatted}. This sign-up has been removed.",
                from_email=None,
                recipient_list=(signup.student.email,),
                fail_silently=True,
            )

        self.perform_destroy(signup)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=["POST"])
    def delete_multiple(self, request):
        signup_ids = request.POST.getlist("id")
        signups = ClassPeriodSignUp.objects.filter(id__in=signup_ids).select_related(
            "student", "class_period"
        )

        # Determines if any signups were found.
        if signups.exists():
            messages = []
            now = timezone.localdate(timezone.now())
            for signup in signups:
                student = signup.student
                period = signup.class_period
                # If associated periods are in the present/future, then emails will be
                # sent to notify students of the removal of their signups.
                if period.date >= now:
                    period_date_formatted = date_format(period.date, DATE_FORMAT)
                    messages.append(
                        (
                            "Media Center Sign-Up Removal",
                            f"You signed up to use the Holy Cross Media Center during period {period.number} on {period_date_formatted}. This sign-up has been removed.",
                            None,
                            (student.email,),
                        )
                    )
            send_mass_mail(messages, fail_silently=True)

            signups.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)

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
