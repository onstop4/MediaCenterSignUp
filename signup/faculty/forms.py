from datetime import timedelta

from django import forms
from django.conf import settings
from django.utils import timezone


class FutureClassPeriodsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Date should be tomorrow by default.
        tomorrow_date = timezone.now() + timedelta(days=1)
        self.fields["date"] = forms.DateField(label="Date", initial=tomorrow_date)

        for number in range(1, settings.MAX_PERIOD_NUMBER + 1):
            self.fields[f"period_{number}"] = forms.IntegerField(
                label=f"Period {number}", min_value=0, initial=0
            )
