from django.conf import settings
from django.urls import reverse
from requests_oauthlib import OAuth2Session

from signup.auth import UserDetails

AUTHORIZATION_BASE_URL = "https://accounts.google.com/o/oauth2/v2/auth"

scope = [
    "openid",
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
]


def generate_oauth_object(request) -> OAuth2Session:
    """Generates an :class:`OAuth2Session` object for logging users in with Google."""
    redirect_uri = request.build_absolute_uri(reverse("google_callback"))
    return OAuth2Session(
        settings.GOOGLE_CLIENT_ID, scope=scope, redirect_uri=redirect_uri
    )


def generate_authorization_url(request):
    """Generates an authorization URL using the base URL provided by Google."""
    google = generate_oauth_object(request)
    authorization_url, state = google.authorization_url(
        AUTHORIZATION_BASE_URL, prompt="select_account"
    )
    return authorization_url, state


def get_user_details(request) -> OAuth2Session:
    """Uses ``callback_url`` to complete the OAuth2 process and retrieve information
    about the user."""
    google = generate_oauth_object(request)
    google.fetch_token(
        "https://accounts.google.com/o/oauth2/token",
        authorization_response=request.build_absolute_uri(),
        client_secret=settings.GOOGLE_CLIENT_SECRET,
    )
    response = google.get("https://www.googleapis.com/oauth2/v1/userinfo")
    json = response.json()
    return UserDetails(json.get("email"), json.get("name"))
