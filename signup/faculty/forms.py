from constance import config
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
        initial = kwargs.get("initial", {})

        self.fields["date"] = forms.DateField(
            label="Date", initial=initial.get("date"), widget=DateInput
        )

        for number in range(1, config.MAX_PERIOD_NUMBER + 1):
            self.fields[f"period_{number}"] = forms.IntegerField(
                label=f"Period {number}",
                min_value=0,
                # If form is created with an initial value for a specific period, use
                # that value. Otherwise, just use zero.
                initial=initial.get(f"period_{number}", 0),
            )


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
