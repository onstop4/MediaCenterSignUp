from django.urls import include, path
from rest_framework.routers import DefaultRouter

from signup.faculty.api.views import ClassPeriodSignUpViewSet

router = DefaultRouter()
router.register("signups", ClassPeriodSignUpViewSet, basename="api-signups")

urlpatterns = [path("", include(router.urls))]
