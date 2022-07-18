from typing import NamedTuple, Optional

from django.contrib.auth.backends import BaseBackend

from signup.models import Student, User


class UserDetails(NamedTuple):
    """Stores user information retrived from OAuth provider."""

    email: str
    name: str


class OAuthBackend(BaseBackend):
    """Authenticates against ``user_details``, which should contain details about a user
    that are returned from an OAuth provider. Does not handle OAuth process itself. The
    email address must end with "@myhchs.org"."""

    def authenticate(self, request, user_details: Optional[UserDetails] = None):
        # pylint: disable=arguments-differ
        if user_details is not None:
            email, name = user_details
            is_hchs_person = email.lower().endswith("@myhchs.org")
            if is_hchs_person:
                try:
                    user = User.objects.get(email=email)
                except User.DoesNotExist:
                    user = Student(email=email, name=name)
                    user.save()
                if self.user_can_authenticate(user):
                    return user

        return None

    def get_user(self, user_id):
        try:
            user = User.objects.get(pk=user_id)
            return user if self.user_can_authenticate(user) else None
        except User.DoesNotExist:
            return None

    def user_can_authenticate(self, user):
        return user.is_active
