from django import forms
from django.conf import settings
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
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Gets all class periods occuring today that haven't reached student capacity
        # yet.
        available_periods = ClassPeriod.objects.annotate(
            signed_up_count=Count("student_sign_ups")
        ).filter(date=timezone.now(), signed_up_count__lt=F("max_student_count"))

        for period in available_periods:
            # Uses ChoiceField if student can sign up for lunch. Otherwise, uses
            # BooleanField.
            if (
                settings.LUNCH_PERIODS_START
                <= period.number
                <= settings.LUNCH_PERIODS_END
            ):
                choices = ClassPeriodSignUp.REASON_TYPES
                new_field = forms.ChoiceField(
                    choices=choices, widget=forms.RadioSelect, required=False
                )
            else:
                new_field = forms.BooleanField(required=False)

            new_field.label = f"Period {period.number}"
            self.fields[f"period_{period.number}"] = new_field
