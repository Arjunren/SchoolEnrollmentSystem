from django.db.models import Count, Q
from rest_framework import permissions, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from core.permissions import IsRegistrar
from .models import Course, Enrollment, Program, Section, StudentProfile, Term
from .serializers import CourseSerializer, EnrollmentSerializer, ProgramSerializer, SectionSerializer, StudentSerializer, TermSerializer
from .services import record_grade


class RegistrarWriteMixin:
    def get_permissions(self):
        return [IsRegistrar()] if self.action in {"create", "update", "partial_update", "destroy"} else [permissions.IsAuthenticated()]


class ProgramViewSet(RegistrarWriteMixin, viewsets.ModelViewSet):
    queryset = Program.objects.all().order_by("code")
    serializer_class = ProgramSerializer
    search_fields = ["code", "name"]


class CourseViewSet(RegistrarWriteMixin, viewsets.ModelViewSet):
    queryset = Course.objects.select_related("program").all().order_by("code")
    serializer_class = CourseSerializer
    search_fields = ["code", "title"]
    filterset_fields = ["program"]


class TermViewSet(RegistrarWriteMixin, viewsets.ModelViewSet):
    queryset = Term.objects.all().order_by("-starts_on")
    serializer_class = TermSerializer


class SectionViewSet(RegistrarWriteMixin, viewsets.ModelViewSet):
    queryset = Section.objects.select_related("course", "term", "teacher").annotate(enrolled_count=Count("enrollments", filter=Q(enrollments__status="enrolled")))
    serializer_class = SectionSerializer
    search_fields = ["code", "course__code", "course__title", "teacher__last_name"]
    ordering_fields = ["code", "capacity", "created_at"]


class StudentViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = StudentSerializer
    search_fields = ["student_number", "user__first_name", "user__last_name", "user__email"]

    def get_queryset(self):
        queryset = StudentProfile.objects.select_related("user", "program")
        return queryset.filter(user=self.request.user) if self.request.user.role == "student" else queryset


class EnrollmentViewSet(viewsets.ModelViewSet):
    serializer_class = EnrollmentSerializer
    http_method_names = ["get", "post", "patch", "head", "options"]
    search_fields = ["student__student_number", "section__course__code"]
    ordering_fields = ["created_at", "grade"]

    def get_queryset(self):
        queryset = Enrollment.objects.select_related("student__user", "section__course", "section__teacher", "created_by").order_by("-created_at")
        user = self.request.user
        if user.role == "student":
            return queryset.filter(student__user=user)
        if user.role == "teacher":
            return queryset.filter(section__teacher=user)
        return queryset

    @action(detail=True, methods=["patch"])
    def grade(self, request, pk=None):
        if request.user.role != "teacher":
            raise PermissionDenied("Only teachers can record grades.")
        value = request.data.get("grade")
        try:
            grade = float(value)
        except (TypeError, ValueError) as exc:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"grade": "A numeric grade is required."}) from exc
        if not 0 <= grade <= 100:
            from rest_framework.exceptions import ValidationError
            raise ValidationError({"grade": "Grade must be between 0 and 100."})
        updated = record_grade(enrollment=self.get_object(), teacher=request.user, grade=grade)
        return Response(self.get_serializer(updated).data)


@api_view(["GET"])
@permission_classes([IsRegistrar])
def dashboard(request):
    return Response({"data": {"students": StudentProfile.objects.count(), "open_terms": Term.objects.filter(enrollment_open=True).count(), "active_enrollments": Enrollment.objects.filter(status="enrolled").count(), "sections": Section.objects.count()}})
