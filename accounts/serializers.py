import secrets

from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from rest_framework import serializers

from academics.models import Program, StudentProfile

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "role", "is_active", "date_joined"]
        read_only_fields = fields


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    program = serializers.PrimaryKeyRelatedField(queryset=Program.objects.all(), write_only=True)

    class Meta:
        model = User
        fields = ["username", "email", "password", "first_name", "last_name", "program"]

    @transaction.atomic
    def create(self, validated_data):
        program = validated_data.pop("program")
        user = User.objects.create_user(**validated_data, role="student")
        StudentProfile.objects.create(user=user, program=program, student_number=f"STU-{secrets.token_hex(5).upper()}")
        return user
