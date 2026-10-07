from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone

from academics.models import Course, Program, Section, StudentProfile, Term


class Command(BaseCommand):
    @transaction.atomic
    def handle(self, *args, **options):
        User = get_user_model()
        admin, _ = User.objects.get_or_create(username="admin", defaults={"email": "admin@example.com", "role": "admin", "is_staff": True, "is_superuser": True})
        teacher, _ = User.objects.get_or_create(username="teacher", defaults={"email": "teacher@example.com", "role": "teacher"})
        student, _ = User.objects.get_or_create(username="student", defaults={"email": "student@example.com", "role": "student"})
        for user in [admin, teacher, student]:
            user.set_password("ChangeMe123!")
            user.save()
        program, _ = Program.objects.get_or_create(code="BSCS", defaults={"name": "Bachelor of Science in Computer Science"})
        course, _ = Course.objects.get_or_create(code="CS101", defaults={"title": "Introduction to Computing", "units": 3, "program": program})
        term, _ = Term.objects.get_or_create(name="2026 Fall", defaults={"starts_on": timezone.localdate(), "ends_on": timezone.localdate() + timedelta(days=120), "enrollment_open": True})
        Section.objects.get_or_create(term=term, code="A", defaults={"course": course, "teacher": teacher, "capacity": 30, "schedule": "Mon/Wed 09:00"})
        StudentProfile.objects.get_or_create(user=student, defaults={"student_number": "STU-DEMO001", "program": program})
        self.stdout.write(self.style.SUCCESS("Sample data loaded"))
