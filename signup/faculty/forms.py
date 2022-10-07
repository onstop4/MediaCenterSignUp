from constance import config
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _


# See https://stackoverflow.com/a/22846522 for more info.
class DateInput(forms.DateInput):
    """Forces Django to render form using HTML5's date input field."""

    input_type = "date"


class FutureClassPeriodsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.template_pack = "bootstrap5"

        initial = kwargs.get("initial", {})
        self.existing_periods = initial.get("existing_periods", {})

        self.fields["date"] = forms.DateField(
            label="Date", initial=initial.get("date"), widget=DateInput
        )

        for number in range(1, config.MAX_PERIOD_NUMBER + 1):
            period = self.existing_periods.get(number)
            self.fields[f"period_{number}"] = forms.IntegerField(
                label=f"Period {number}",
                min_value=0,
                # If form is created with an initial value for a specific period, use
                # that value. Otherwise, just use zero.
                initial=period.max_student_count if period else 0,
            )

        self.helper.add_input(Submit("submit", "Submit"))

    def clean(self):
        cleaned_data = super().clean()
        errors = []

        for number in range(1, config.MAX_PERIOD_NUMBER):
            if period := self.existing_periods.get(number):
                new_max_student_count = cleaned_data[f"period_{number}"]
                current_count = period.student_sign_ups.count()

                if current_count > new_max_student_count:
                    errors.append(
                        ValidationError(
                            f"Period {number} currently has {current_count} students, which is greater than the new maximum of {new_max_student_count}."
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        self.helper.template_pack = "bootstrap5"

        self.helper.add_input(Submit("submit", "Submit"))

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
