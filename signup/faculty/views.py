from itertools import groupby

from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import FormView, ListView

from signup.faculty.forms import FutureClassPeriodsForm
from signup.models import ClassPeriod


class ClassPeriodsListView(ListView):
    template_name = "faculty/periods_list.html"
    context_object_name = "periods_grouped"
    future = True

    def get_queryset(self):
        periods = ClassPeriod.objects.get_queryset_unordered()

        # If self.past is True, then list class periods frm the past. Otherwise, list
        # class periods today and in the future.
        periods = (
            periods.filter(date__gte=timezone.now())
            if self.future
            else periods.filter(date__lt=timezone.now())
        )

        # Groups ClassPeriod objects by date so that the max student counts of each
        # separate ClassPeriod object can be presented together in the template.
        periods = periods.order_by("date" if self.future else "-date", "number")
        periods_counted = periods.count()
        periods_grouped = groupby(periods, lambda period: period.date)

        # When rendering for-loops in templates, Django will call len() on iterables.
        # When it can't call len() (because __len__ does not exist), it will convert the
        # iterable into a list. This conflicts with the logic behind itertools.groupby,
        # where each iteration causes the previous iteration to be lost. Because of this
        # I am returning an instance of the class below instead since its __len__ won't
        # cause problems with itertools.groupby. See
        # https://stackoverflow.com/a/16171518 for more info.
        class GroupedPeriods:
            def __len__(self):
                return periods_counted

            def __iter__(self):
                return periods_grouped

        return GroupedPeriods()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Adds range of period numbers to context for first row of grid.
        context["period_numbers"] = range(1, settings.MAX_PERIOD_NUMBER + 1)

        # Adjusts some text on template based on whether the view is supposed to show
        # periods today and in the future OR just periods in the past.
        context["future"] = self.future

        # Adds today's date to context so special text can be printed when a set of
        # max student counts is for today.
        context["date_today"] = timezone.now().date()

        return context


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
