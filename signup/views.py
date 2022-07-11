from django.contrib.auth import authenticate, login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView

from signup.forms import StudentInfoForm
from signup.google_oauth import generate_authorization_url, get_user_details
from signup.models import student_has_info


def index(request):
    user = request.user
    if user.is_authenticated:
        return redirect("student_form")

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


class UserNeedsLoginMixin(LoginRequiredMixin):
    """Ensures that anonymous users are redirected to the index. Normally, this can be
    accomplished just by setting ``LOGIN_URL`` in the project settings, but this mixin
    ensures that the "next" parameter isn't part of the URL."""

    # See https://stackoverflow.com/q/63566841/ for more info.
    redirect_field_name = None


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


class StudentSignUpFormView(StudentNeedsInfoMixin, TemplateView):
    template_name = "signup/student_sign_up_form.html"


class StudentInfoFormView(UserNeedsLoginMixin, CreateView):
    template_name = "signup/student_info_form.html"
    form_class = StudentInfoForm
    success_url = reverse_lazy("student_sign_up_form")

    def form_valid(self, form):
        form.instance.student = self.request.user
        form.save()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        # Essentially the opposite of StudentNeedsInfoMixin. If student is authenticated
        # and has filled out the form, then they will be redirected to the sign-up form.
        # If they haven't filled out the form, then CreateView will handle response. If
        # user is not authenticated, then user will be redirected to index.
        user = request.user
        if user.is_authenticated and student_has_info(user):
            return redirect(reverse("student_sign_up_form"))
        return super().dispatch(request, *args, **kwargs)
