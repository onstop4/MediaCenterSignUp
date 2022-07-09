from django.urls import path

from signup.views import google_callback, index, student_form

urlpatterns = [
    path("", index, name="index"),
    path("callback/", google_callback, name="google_callback"),
    path("s/", student_form, name="student_form"),
]
