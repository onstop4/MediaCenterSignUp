from constance import config
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError
from django.db.models import Count
from django.utils.translation import gettext_lazy as _

from signup.models import ClassPeriodSignUp


# Taken from https://stackoverflow.com/a/59893460.
class HiddenInput(forms.Widget):
    input_type = "hidden"

    template_name = ""

    def render(self, name, value, attrs=None, renderer=None):
        return ""


class FutureClassPeriodsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.template_pack = "bootstrap5"

        initial = kwargs.get("initial", {})
        self.existing_periods = initial.get("existing_periods", {})

        self.fields["start_date"] = forms.DateField(widget=HiddenInput, required=True)
        self.fields["end_date"] = forms.DateField(widget=HiddenInput, required=False)

        for number in range(1, config.MAX_PERIOD_NUMBER + 1):
            period = self.existing_periods.get(number)
            self.fields[f"period_{number}"] = forms.IntegerField(
                label=f"Period {number}",
                min_value=0,
                # If form is created with an initial value for a specific period, use
                # that value. Otherwise, just use zero.
                initial=period.max_student_count if period else 0,
            )

    def clean(self):
        cleaned_data = super().clean()
        errors = []

        start_date = cleaned_data.get("start_date")

        if start_date is None:
            errors.append("You must enter a start date.")
        else:
            end_date = cleaned_data["end_date"] = (
                cleaned_data.get("end_date") or start_date
            )

            if end_date < start_date:
                errors.append("Start date must come before end date.")

        for number in range(1, config.MAX_PERIOD_NUMBER):
            if cleaned_data.get(f"period_{number}") is None:
                errors.append(f"The input for period {number} is invalid.")

        if errors:
            raise ValidationError(errors)

        signups = (
            ClassPeriodSignUp.objects.filter(
                class_period__date__gte=start_date, class_period__date__lte=end_date
            )
            .values(
                "class_period__date",
                "class_period__number",
                "class_period__max_student_count",
            )
            .annotate(period_count=Count("class_period__pk"))
            .order_by("class_period__date", "class_period__number")
        )

        for signup in signups:
            period_count = signup["period_count"]
            class_period_number = signup["class_period__number"]
            class_period_date = signup["class_period__date"]
            new_max_student_count = cleaned_data[f"period_{class_period_number}"]
            if period_count > new_max_student_count:
                errors.append(
                    ValidationError(
                        f"Period {class_period_number} on {class_period_date} currently has {period_count} students, which is greater than the new maximum of {new_max_student_count}."
                    )
                )

        if errors:
            raise ValidationError(errors)


class SettingsForm(forms.Form):
    max_period_number = forms.IntegerField(label=_("Max number of periods"))
    sign_up_form_opens_time = forms.TimeField(label=_("Time sign-up form opens"))
    sign_up_form_closes_time = forms.TimeField(label=_("Time sign-up form closes"))
    force_open_sign_up_form = forms.BooleanField(
        label=_("Force sign-up form to be open"), required=False
    )
    lunch_periods_start = forms.IntegerField(label=_("First lunch period"))
    lunch_periods_end = forms.IntegerField(label=_("Last lunch period"))

    def clean(self):
        cleaned_data = super().clean()
        errors = []

        if (
            cleaned_data["sign_up_form_opens_time"]
            >= cleaned_data["sign_up_form_closes_time"]
        ):
            errors.append(
                ValidationError(
                    "The time that the form closes must come after the time that the "
                    "form closes."
                )
            )

        if cleaned_data["lunch_periods_start"] > cleaned_data["lunch_periods_end"]:
            errors.append(
                "The last lunch period must not come before the first lunch period."
            )

        if errors:
            raise ValidationError(errors)

        return cleaned_data
