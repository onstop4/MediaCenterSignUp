from constance import config
from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, FormView, TemplateView

from signup.forms import StudentInfoForm, StudentSignUpForm
from signup.google_oauth import generate_authorization_url, get_user_details
from signup.models import (
    ClassPeriod,
    ClassPeriodSignUp,
    is_library_faculty_member,
    student_has_info,
)


def index(request):
    user = request.user
    if user.is_authenticated:
        return redirect("student_sign_up_form")

    authorization_url, state = generate_authorization_url(request)
    request.session["oauth_state"] = state

    return render(
        request, "signup/login.html", {"authorization_url": authorization_url}
    )


def google_callback(request):
    user_details = get_user_details(request)
    user = authenticate(request, user_details=user_details)

    if user:
        login(request, user)
        return redirect("student_sign_up_form")
    return render(request, "signup/login_failed.html", {})


def robots_txt(request):
    # Adapted from https://stackoverflow.com/a/39662564.
    return HttpResponse("User-Agent: *\nDisallow: /", content_type="text/plain")


class UserNeedsLoginMixin(LoginRequiredMixin):
    """Ensures that anonymous users are redirected to the index. Normally, this can be
    accomplished just by setting ``LOGIN_URL`` in the project settings, but this mixin
    ensures that the "next" parameter isn't part of the URL.

    Also ensures that faculty members are redirected to one of their views."""

    # See https://stackoverflow.com/q/63566841/ for more info.
    redirect_field_name = None

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and is_library_faculty_member(user):
            return redirect(reverse("faculty_index"))

        return super().dispatch(request, *args, **kwargs)


class StudentNeedsInfoMixin(UserNeedsLoginMixin):
    """Ensures that students that haven't filled out the student info form will be
    redirected so they can fill out the form."""

    def dispatch(self, request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and not student_has_info(user):
            return redirect(reverse("student_info_form"))

        # If user is not authenticated, then super().dispatch will redirect user to
        # index. If student is authenticated and has filled out the form, then
        # this class and subclass will not redirect student.
        return super().dispatch(request, *args, **kwargs)


class StudentFormMixin:
    """Ensures that a :class:`ModelForm` whose model can only be saved with a Student
    object is saved with the currently logged-in student."""

    def form_valid(self, form):
        form.instance.student = self.request.user
        form.save()
        return super().form_valid(form)


class StudentInfoFormView(UserNeedsLoginMixin, StudentFormMixin, CreateView):
    template_name = "signup/student_info_form.html"
    form_class = StudentInfoForm
    success_url = reverse_lazy("student_sign_up_form")

    def dispatch(self, request, *args, **kwargs):
        # Essentially the opposite of StudentNeedsInfoMixin. If student is authenticated
        # and has filled out the form, then they will be redirected to the sign-up form.
        # If they haven't filled out the form, then CreateView will handle response. If
        # user is not authenticated, then user will be redirected to index.
        user = request.user
        if user.is_authenticated and student_has_info(user):
            return redirect(reverse("student_sign_up_form"))
        return super().dispatch(request, *args, **kwargs)


class StudentSignUpOpenMixin:
    """Only allows request to complete normally if form is open depending on the values
    of ``SIGN_UP_FORM_OPENS_TIME``, ``SIGN_UP_FORM_CLOSES_TIME``, and
    ``FORCE_OPEN_SIGN_UP_FORM`` in the Constance settings."""

    def is_open(self) -> bool:
        """Determines if the form is open now according to the values of
        ``SIGN_UP_FORM_OPENS_TIME`` and ``SIGN_UP_FORM_CLOSES_TIME`` in the project
        settings."""
        time_now_naive = timezone.localtime(timezone.now()).time()
        return (
            config.SIGN_UP_FORM_OPENS_TIME
            <= time_now_naive
            < config.SIGN_UP_FORM_CLOSES_TIME
        )

    def dispatch(self, request, *args, **kwargs):
        if config.FORCE_OPEN_SIGN_UP_FORM or self.is_open():
            return super().dispatch(request, *args, **kwargs)
        return render(
            request,
            "signup/student_sign_up_form_closed.html",
            {
                "form_time_opens": config.SIGN_UP_FORM_OPENS_TIME,
                "form_time_closes": config.SIGN_UP_FORM_CLOSES_TIME,
            },
        )


class StudentSignUpFormView(StudentNeedsInfoMixin, StudentSignUpOpenMixin, FormView):
    template_name = "signup/student_sign_up_form.html"
    success_url = reverse_lazy("student_sign_up_success")

    def get_form(self, form_class=None):
        return StudentSignUpForm(student=self.request.user, **self.get_form_kwargs())

    def form_valid(self, form):
        for period in form.available_periods:
            number = period.number
            # Checks if period was part of form.
            yes = form.cleaned_data.get(f"period_{number}", False)
            if yes:
                # If lunch period, use student's choice. Otherwise, just use
                # ClassPeriodSignUp.STUDY_HALL. That way, a student cannot indicate that
                # they are using the library for a lunch period when that period isn't a
                # lunch period.
                if period.is_lunch_period():
                    reason = yes
                else:
                    reason = ClassPeriodSignUp.STUDY_HALL
                ClassPeriodSignUp.objects.create(
                    student=self.request.user,
                    class_period=period,
                    reason=reason,
                )

        return super().form_valid(form)


class StudentSignUpSuccessView(StudentNeedsInfoMixin, TemplateView):
    template_name = "signup/student_sign_up_success.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        student = self.request.user
        today = timezone.now()

        # Allows template to list all the periods that the student signed up for today.
        context["periods"] = ClassPeriod.objects.filter(
            student_sign_ups__student=student,
            student_sign_ups__date_signed_up__date=today,
        ).all()

        return context
