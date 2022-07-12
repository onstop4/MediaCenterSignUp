from django.urls import path

from signup.views import (
    StudentInfoFormView,
    StudentSignUpFormView,
    google_callback,
    index,
    student_sign_up_success,
)

urlpatterns = [
    path("", index, name="index"),
    path("callback/", google_callback, name="google_callback"),
    path("s/", StudentSignUpFormView.as_view(), name="student_sign_up_form"),
    path("s/info/", StudentInfoFormView.as_view(), name="student_info_form"),
    path("s/success/", student_sign_up_success, name="student_sign_up_success"),
]
