import django_filters

from signup.models import ClassPeriodSignUp

fields = [
    "id",
    "class_period__number",
    "class_period__date",
    "student__name",
    "student__id",
    "date_signed_up",
    "reason",
    "attendance_confirmed",
    "date_attendance_confirmed",
]


class ClassPeriodSignUpFilter(django_filters.FilterSet):
    class Meta:
        model = ClassPeriodSignUp
        fields = fields
