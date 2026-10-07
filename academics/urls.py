from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CourseViewSet, EnrollmentViewSet, ProgramViewSet, SectionViewSet, StudentViewSet, TermViewSet, dashboard

router = DefaultRouter()
router.register("programs", ProgramViewSet)
router.register("courses", CourseViewSet)
router.register("terms", TermViewSet)
router.register("sections", SectionViewSet)
router.register("students", StudentViewSet, basename="student")
router.register("enrollments", EnrollmentViewSet, basename="enrollment")
urlpatterns = [path("", include(router.urls)), path("dashboard/", dashboard)]
