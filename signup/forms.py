from constance import config
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Count, F
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from signup.models import ClassPeriod, ClassPeriodSignUp, StudentInfo


class StudentInfoForm(forms.ModelForm):
    class Meta:
        model = StudentInfo
        fields = ["id"]

    def clean_id(self):
        _id = self.cleaned_data.get("id", None)
        if _id and _id.isdigit():
            return _id
        raise ValidationError(_("ID can only contain digits."))


class StudentSignUpForm(forms.Form):
    def __init__(self, *args, student=None, **kwargs):
        super().__init__(*args, **kwargs)

        now = timezone.now()

        # Gets all class periods occuring today that haven't reached student capacity
        # yet. Stores result as instance variable so it can be accessed by
        # StudentSignUpFormView.
        self.available_periods = ClassPeriod.objects.annotate(
            signed_up_count=Count("student_sign_ups")
        ).filter(date=now, signed_up_count__lt=F("max_student_count"))

        # Excludes periods that the student has already signed up for.
        if student:
            signed_up_already = student.sign_ups.filter(class_period__date=now)
            self.available_periods = self.available_periods.exclude(
                student_sign_ups__in=signed_up_already
            )

        self.available_periods = self.available_periods.all()

        for period in self.available_periods:
            # Uses ChoiceField if student can sign up for lunch. Otherwise, uses
            # BooleanField.
            if config.LUNCH_PERIODS_START <= period.number <= config.LUNCH_PERIODS_END:
                choices = ClassPeriodSignUp.REASON_TYPES
                new_field = forms.ChoiceField(
                    choices=choices, widget=forms.RadioSelect, required=False
                )
            else:
                new_field = forms.BooleanField(required=False)

            new_field.label = f"Period {period.number}"
            self.fields[f"period_{period.number}"] = new_field
