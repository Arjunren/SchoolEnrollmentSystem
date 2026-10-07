from rest_framework import serializers

from accounts.serializers import UserSerializer
from .models import Course, Enrollment, Program, Section, StudentProfile, Term
from .services import enroll_student


class ProgramSerializer(serializers.ModelSerializer):
    class Meta:
        model = Program
        fields = "__all__"
        read_only_fields = ["created_at"]


class CourseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = "__all__"
        read_only_fields = ["created_at"]


class TermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Term
        fields = "__all__"

    def validate(self, attrs):
        starts_on = attrs.get("starts_on", getattr(self.instance, "starts_on", None))
        ends_on = attrs.get("ends_on", getattr(self.instance, "ends_on", None))
        if ends_on <= starts_on:
            raise serializers.ValidationError("Term end date must be after start date.")
        return attrs


class SectionSerializer(serializers.ModelSerializer):
    enrolled_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Section
        fields = ["id", "course", "term", "teacher", "code", "capacity", "schedule", "enrolled_count", "created_at"]
        read_only_fields = ["created_at"]


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = StudentProfile
        fields = ["id", "user", "student_number", "program", "year_level", "created_at"]


class EnrollmentSerializer(serializers.ModelSerializer):
    student = serializers.PrimaryKeyRelatedField(queryset=StudentProfile.objects.all(), required=False)

    class Meta:
        model = Enrollment
        fields = ["id", "student", "section", "status", "grade", "created_by", "created_at", "updated_at"]
        read_only_fields = ["status", "grade", "created_by", "created_at", "updated_at"]

    def create(self, validated_data):
        request = self.context["request"]
        if request.user.role == "student":
            validated_data["student"] = request.user.student_profile
        elif "student" not in validated_data:
            raise serializers.ValidationError({"student": "This field is required."})
        return enroll_student(actor=request.user, **validated_data)
