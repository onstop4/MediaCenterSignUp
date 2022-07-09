from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render

from signup.google_oauth import generate_authorization_url, get_user_details


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
        return redirect("student_form")
    return render(request, "signup/login_failed.html", {})


def student_form(request):
    pass
