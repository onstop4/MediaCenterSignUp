from django import forms
from django.conf import settings


class FutureClassPeriodsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        initial = kwargs.get("initial", {})

        self.fields["date"] = forms.DateField(label="Date", initial=initial.get("date"))

        for number in range(1, settings.MAX_PERIOD_NUMBER + 1):
            self.fields[f"period_{number}"] = forms.IntegerField(
                label=f"Period {number}",
                min_value=0,
                # If form is created with an initial value for a specific period, use
                # that value. Otherwise, just use zero.
                initial=initial.get(f"period_{number}", 0),
            )
