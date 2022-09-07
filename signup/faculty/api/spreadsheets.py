from django.utils import timezone
from openpyxl import Workbook

from signup.models import StudentInfo


def generate_spreadsheet(signups):
    """Generates spreadsheet (Excel workbook)."""
    signups = signups.select_related(
        "student", "student__info", "class_period"
    ).order_by("class_period__date", "class_period__number", "student__name")

    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Student Sign-Ups"

    sheet.append(
        [
            "Date",
            "Period Number",
            "Student Name",
            "Student ID",
            "Reason",
            "Date Signed Up",
            "Attendance Confirmed",
            "Date Attendance Confirmed",
        ]
    )

    for signup in signups:
        # Handles the event that a StudentInfo object does not exist for the Student,
        # which should never occur during normal usage.
        try:
            student_id = signup.student.info.id
        except StudentInfo.DoesNotExist:
            student_id = None

        # Adds signup details to workbook.
        sheet.append(
            [
                signup.class_period.date,
                signup.class_period.number,
                signup.student.name,
                student_id,
                signup.get_reason_display(),
                timezone.localtime(signup.date_signed_up).replace(tzinfo=None),
                signup.attendance_confirmed,
                timezone.localtime(signup.date_attendance_confirmed).replace(
                    tzinfo=None
                ),
            ]
        )

    return workbook
