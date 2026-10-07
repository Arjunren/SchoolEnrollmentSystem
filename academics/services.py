from django.db import IntegrityError, transaction
from rest_framework.exceptions import ValidationError

from .models import Enrollment, Section


@transaction.atomic
def enroll_student(*, student, section, actor):
    locked = Section.objects.select_for_update().select_related("term").get(pk=section.pk)
    if not locked.term.enrollment_open:
        raise ValidationError({"section": "Enrollment is closed for this term."})
    occupied = Enrollment.objects.filter(section=locked, status=Enrollment.Status.ENROLLED).count()
    if occupied >= locked.capacity:
        raise ValidationError({"section": "Section is full."})
    try:
        return Enrollment.objects.create(student=student, section=locked, created_by=actor)
    except IntegrityError as exc:
        raise ValidationError({"section": "Student is already enrolled in this section."}) from exc


@transaction.atomic
def record_grade(*, enrollment, teacher, grade):
    locked = Enrollment.objects.select_for_update().select_related("section").get(pk=enrollment.pk)
    if locked.section.teacher_id != teacher.id:
        raise ValidationError({"grade": "Only the assigned teacher may record this grade."})
    if locked.status != Enrollment.Status.ENROLLED:
        raise ValidationError({"status": "Only active enrollments can be graded."})
    locked.grade = grade
    locked.status = Enrollment.Status.COMPLETED
    locked.save(update_fields=["grade", "status", "updated_at"])
    return locked
