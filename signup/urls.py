from django.urls import path

from signup.views import (
    StudentInfoFormView,
    StudentSignUpFormView,
    StudentSignUpSuccessView,
    google_callback,
    index,
)

urlpatterns = [
    path("", index, name="index"),
    path("callback/", google_callback, name="google_callback"),
    path("s/", StudentSignUpFormView.as_view(), name="student_sign_up_form"),
    path("s/info/", StudentInfoFormView.as_view(), name="student_info_form"),
    path(
        "s/success/", StudentSignUpSuccessView.as_view(), name="student_sign_up_success"
    ),
]
