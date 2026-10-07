from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework.test import APIClient

from academics.models import Course, Enrollment, Program, Section, StudentProfile, Term

User = get_user_model()


@pytest.fixture
def client(): return APIClient()


@pytest.fixture
def program(db): return Program.objects.create(code="BSCS", name="Computer Science")


@pytest.fixture
def teacher(db): return User.objects.create_user("teacher", "teacher@example.com", "StrongPass123!", role="teacher")


@pytest.fixture
def student(db, program):
    user = User.objects.create_user("student", "student@example.com", "StrongPass123!", role="student")
    StudentProfile.objects.create(user=user, student_number="STU-001", program=program)
    return user


@pytest.fixture
def section(db, program, teacher):
    course = Course.objects.create(code="CS101", title="Computing", units=3, program=program)
    term = Term.objects.create(name="Fall", starts_on=timezone.localdate(), ends_on=timezone.localdate() + timedelta(days=90), enrollment_open=True)
    return Section.objects.create(course=course, term=term, teacher=teacher, code="A", capacity=1, schedule="Monday 09:00")


@pytest.mark.django_db
def test_registration_forces_student_role(client, program):
    response = client.post("/api/auth/register/", {"username": "new", "email": "new@example.com", "password": "StrongPass123!", "program": program.id, "role": "admin"}, format="json")
    assert response.status_code == 201
    assert response.data["data"]["user"]["role"] == "student"
    assert StudentProfile.objects.filter(user__username="new").exists()


@pytest.mark.django_db
def test_student_enrolls_self_even_when_other_student_is_submitted(client, student, section, program):
    other = User.objects.create_user("other", "other@example.com", "StrongPass123!", role="student")
    other_profile = StudentProfile.objects.create(user=other, student_number="STU-002", program=program)
    client.force_authenticate(student)
    response = client.post("/api/enrollments/", {"student": other_profile.id, "section": section.id}, format="json")
    assert response.status_code == 201
    assert response.data["student"] == student.student_profile.id


@pytest.mark.django_db
def test_section_capacity_is_enforced(client, student, section, program):
    Enrollment.objects.create(student=student.student_profile, section=section, created_by=student)
    other = User.objects.create_user("other", "other@example.com", "StrongPass123!", role="student")
    StudentProfile.objects.create(user=other, student_number="STU-002", program=program)
    client.force_authenticate(other)
    response = client.post("/api/enrollments/", {"section": section.id}, format="json")
    assert response.status_code == 400
    assert response.data["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.django_db
def test_student_only_sees_own_enrollments(client, student, section, program):
    Enrollment.objects.create(student=student.student_profile, section=section, created_by=student)
    other = User.objects.create_user("other", "other@example.com", "StrongPass123!", role="student")
    other_profile = StudentProfile.objects.create(user=other, student_number="STU-002", program=program)
    other_section = Section.objects.create(course=section.course, term=section.term, teacher=section.teacher, code="B", capacity=2, schedule="Tuesday")
    Enrollment.objects.create(student=other_profile, section=other_section, created_by=other)
    client.force_authenticate(student)
    response = client.get("/api/enrollments/")
    assert response.status_code == 200
    assert response.data["count"] == 1


@pytest.mark.django_db
def test_only_assigned_teacher_can_record_grade(client, student, section, teacher):
    enrollment = Enrollment.objects.create(student=student.student_profile, section=section, created_by=student)
    other_teacher = User.objects.create_user("otherteacher", "otherteacher@example.com", "StrongPass123!", role="teacher")
    client.force_authenticate(other_teacher)
    assert client.patch(f"/api/enrollments/{enrollment.id}/grade/", {"grade": 90}, format="json").status_code == 404
    client.force_authenticate(teacher)
    response = client.patch(f"/api/enrollments/{enrollment.id}/grade/", {"grade": 90}, format="json")
    assert response.status_code == 200
    assert response.data["status"] == "completed"
    assert response.data["grade"] == "90.00"
