from django.contrib.auth.views import logout_then_login
from django.urls import include, path

from signup.views import (
    LoginFailureView,
    StudentInfoFormView,
    StudentSignUpFormView,
    StudentSignUpSuccessView,
    google_callback,
    index,
    robots_txt,
)

urlpatterns = [
    path("", index, name="index"),
    path("callback/", google_callback, name="google_callback"),
    path("login-failed/", LoginFailureView.as_view(), name="login_failure"),
    path("logout/", logout_then_login, name="logout"),
    path("robots.txt", robots_txt, name="robots_txt"),
    path("s/", StudentSignUpFormView.as_view(), name="student_sign_up_form"),
    path("s/info/", StudentInfoFormView.as_view(), name="student_info_form"),
    path(
        "s/success/", StudentSignUpSuccessView.as_view(), name="student_sign_up_success"
    ),
    path("f/", include("signup.faculty.urls")),
]
