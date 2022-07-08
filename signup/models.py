from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, **kwargs):
        """Creates a new user."""
        email = self.normalize_email(email)
        user = User(email=email, user_type=self.model.default_user_type, **kwargs)
        user.save()
        return user

    def create_superuser(self, email, **kwargs):
        """Creates a new super user."""
        email = self.normalize_email(email)
        user = User(
            email=email,
            user_type=self.model.default_user_type,
            is_superuser=True,
            **kwargs
        )
        user.save()
        return user

    def get_similar_queryset(self, *args, **kwargs):
        """Returns a queryset containing users with the same user_type as the model's
        default_user_type."""
        return (
            super()
            .get_queryset(*args, **kwargs)
            .filter(user_type=self.model.default_user_type)
        )


class User(AbstractBaseUser, PermissionsMixin):
    objects = UserManager()

    # Represents a student.
    STUDENT = "S"

    # Represents a user who works in the library. This user can edit the class periods
    # and see who signed up for which period. I'm calling this user a "library faculty
    # member" instead of just a "faculty member" just in case I have to support faculty
    # members who don't work in the library in the future.
    LIBRARY_FACULTY_MEMBER = "L"

    USER_TYPES = [
        (STUDENT, _("Student")),
        (LIBRARY_FACULTY_MEMBER, _("Library Faculty Member")),
    ]

    email = models.EmailField(_("email address"), blank=False, unique=True)
    name = models.CharField(_("name"), max_length=150, blank=True)
    is_active = models.BooleanField(
        _("active"),
        default=True,
        help_text=_(
            "Designates whether this user should be treated as active. "
            "Unselect this instead of deleting accounts."
        ),
    )
    date_joined = models.DateTimeField(_("date joined"), default=timezone.now)

    USERNAME_FIELD = "email"

    # Stores the user type as an attribute that proxy tables can edit.
    default_user_type = STUDENT

    user_type = models.CharField(
        max_length=1, choices=USER_TYPES, default=default_user_type
    )


class Student(User):
    class Meta:
        proxy = True

    default_user_type = User.STUDENT


class StudentInfo(models.Model):
    """Stores student information, such as a student's id."""

    student = models.OneToOneField(Student, on_delete=models.CASCADE, primary_key=True)
    id = models.CharField(_("student ID"), unique=True, max_length=10)


class LibraryFacultyMember(User):
    class Meta:
        proxy = True

    default_user_type = User.LIBRARY_FACULTY_MEMBER
