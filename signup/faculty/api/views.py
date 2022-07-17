from rest_framework.generics import ListAPIView, RetrieveUpdateDestroyAPIView

from signup.faculty.api.serializers import ClassPeriodSignUpSerializer
from signup.models import ClassPeriodSignUp


class ClassPeriodSignUpMixin:
    """Contains common logic for the APIViews dealing with :class:`ClassPeriodSignUp`
    objects."""

    queryset = ClassPeriodSignUp.objects.all()
    serializer_class = ClassPeriodSignUpSerializer


class ClassPeriodSignUpListAPIView(ClassPeriodSignUpMixin, ListAPIView):
    pass


class ClassPeriodSignUpDetailAPIView(
    ClassPeriodSignUpMixin, RetrieveUpdateDestroyAPIView
):
    pass
