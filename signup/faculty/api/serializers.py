from rest_framework import serializers

from signup.models import ClassPeriodSignUp


class ClassPeriodSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClassPeriodSignUp
        fields = [
            "id",
            "period_number",
            "student_name",
            "student_id",
            "date_signed_up",
            "reason",
            "attendance_confirmed",
            "date_attendance_confirmed",
        ]

        read_only_fields = [
            "id",
            "date_signed_up",
            "reason",
        ]

        ordering = ["student_name"]

    # I can't include these fields in Meta.read_only_fields above, even though I must
    # include them in Meta.fields. Because of this, I'm specifying "read_only=True" on
    # each of these fields.
    period_number = serializers.IntegerField(
        source="class_period.number", read_only=True
    )
    student_name = serializers.CharField(source="student.name", read_only=True)
    student_id = serializers.CharField(source="student.info.id", read_only=True)
