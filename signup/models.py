from constance import config
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.db import models
from django.db.models.constraints import UniqueConstraint
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **kwargs):
        """Creates a new user."""
        email = self.normalize_email(email)
        user = User(email=email, user_type=self.model.default_user_type, **kwargs)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password=None, **kwargs):
        """Creates a new super user."""
        email = self.normalize_email(email)
        user = User(
            email=email,
            user_type=self.model.default_user_type,
            is_superuser=True,
            **kwargs,
        )
        user.set_password(password)
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

    student = models.OneToOneField(
        Student, on_delete=models.CASCADE, primary_key=True, related_name="info"
    )
    id = models.CharField(_("student ID"), unique=True, max_length=6)


# Function could have been part of Student proxy model, but then I would have difficulty
# casting from a User object to a Student object without an additional database call.
def student_has_info(user):
    """Determines if ``user`` has a corresponding :class:`StudentInfo`."""
    try:
        user.info
    except StudentInfo.DoesNotExist:
        return False
    else:
        return True


class LibraryFacultyMember(User):
    class Meta:
        proxy = True

    default_user_type = User.LIBRARY_FACULTY_MEMBER


def is_library_faculty_member(user):
    """Determines if ``user`` is a library faculty member."""
    return user.is_authenticated and user.user_type == User.LIBRARY_FACULTY_MEMBER


class ClassPeriodManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().order_by("number")

    def get_unordered_queryset(self):
        return super().get_queryset()


class ClassPeriod(models.Model):
    """Represents a class period that students could potentially sign up for."""

    objects = ClassPeriodManager()

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["date", "number"],
                name="unique_date_number",
            )
        ]

    date = models.DateField(_("date"))
    number = models.SmallIntegerField(_("period number"))
    max_student_count = models.PositiveIntegerField(_("maximum students allowed"))

    def is_lunch_period(self):
        return config.LUNCH_PERIODS_START <= self.number <= config.LUNCH_PERIODS_END


class ClassPeriodSignUp(models.Model):
    """
    Represents a student signing up for a specific class period. Also requires student
    to specify if they are signing up because they have lunch or because they have study
    hall.
    """

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=["student", "class_period"],
                name="unique_sign_up_class_period",
            )
        ]

    student = models.ForeignKey(
        Student, on_delete=models.CASCADE, related_name="sign_ups"
    )
    class_period = models.ForeignKey(
        ClassPeriod, on_delete=models.CASCADE, related_name="student_sign_ups"
    )
    date_signed_up = models.DateTimeField(_("date signed up"), default=timezone.now)

    # I could have used Django's built-in support for many-to-many relationships, but
    # then I wouldn't be able to require the "reason" field.
    LUNCH = "L"
    STUDY_HALL = "S"

    REASON_TYPES = [
        (LUNCH, _("lunch")),
        (STUDY_HALL, _("study hall")),
    ]

    reason = models.CharField(max_length=1, choices=REASON_TYPES)

    # Allows library faculty to confirm that a student showed up to the library.
    attendance_confirmed = models.BooleanField(_("attendance confirmed"), default=False)
    date_attendance_confirmed = models.DateTimeField(
        _("date attendance was confirmed"), null=True
    )
