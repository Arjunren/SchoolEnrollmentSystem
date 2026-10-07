from django.conf import settings
from django.db import models


class Program(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=150, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)


class StudentProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_profile")
    student_number = models.CharField(max_length=30, unique=True)
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name="students")
    year_level = models.PositiveSmallIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)


class Course(models.Model):
    code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=180)
    units = models.PositiveSmallIntegerField()
    program = models.ForeignKey(Program, on_delete=models.PROTECT, related_name="courses")
    created_at = models.DateTimeField(auto_now_add=True)


class Term(models.Model):
    name = models.CharField(max_length=80, unique=True)
    starts_on = models.DateField()
    ends_on = models.DateField()
    enrollment_open = models.BooleanField(default=True, db_index=True)


class Section(models.Model):
    course = models.ForeignKey(Course, on_delete=models.PROTECT, related_name="sections")
    term = models.ForeignKey(Term, on_delete=models.PROTECT, related_name="sections")
    teacher = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="teaching_sections")
    code = models.CharField(max_length=20)
    capacity = models.PositiveIntegerField(default=30)
    schedule = models.CharField(max_length=200)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["term", "code"], name="unique_term_section_code")]


class Enrollment(models.Model):
    class Status(models.TextChoices):
        ENROLLED = "enrolled", "Enrolled"
        COMPLETED = "completed", "Completed"
        DROPPED = "dropped", "Dropped"

    student = models.ForeignKey(StudentProfile, on_delete=models.PROTECT, related_name="enrollments")
    section = models.ForeignKey(Section, on_delete=models.PROTECT, related_name="enrollments")
    status = models.CharField(max_length=20, choices=Status, default=Status.ENROLLED, db_index=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="created_enrollments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["student", "section"], name="unique_student_section")]
