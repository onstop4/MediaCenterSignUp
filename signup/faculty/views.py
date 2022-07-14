from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView

from signup.faculty.forms import FutureClassPeriodsForm
from signup.models import ClassPeriod


class FutureClassPeriodsListView(TemplateView):
    template_name = "faculty/future_periods_list.html"


class FutureClassPeriodsFormView(LoginRequiredMixin, FormView):
    template_name = "faculty/future_periods_form.html"
    form_class = FutureClassPeriodsForm
    success_url = reverse_lazy("future_class_periods_list")

    def get_initial(self):
        initial = {}
        date = self.kwargs.get("date")

        if date:
            initial["date"] = date
            # If date is specified in URL, initialize form with max student counts
            # associated with that date (assuming that the form was already filled out
            # for that date).
            periods = ClassPeriod.objects.filter(date=date)

            # If the form was already filled out for a specific date, use the existing
            # values as the form's initial values. Otherwise, the form will use its
            # default initial value, which is zero.
            for period in periods:
                initial[f"period_{period.number}"] = period.max_student_count

        return initial

    def form_valid(self, form):
        date = form.data["date"]
        ClassPeriod.objects.filter(date=date).delete()

        periods = []

        for number in range(1, settings.MAX_PERIOD_NUMBER + 1):
            periods.append(
                ClassPeriod(
                    date=date,
                    number=number,
                    max_student_count=form.data[f"period_{number}"],
                )
            )

        ClassPeriod.objects.bulk_create(periods)

        return super().form_valid(form)
