from django.contrib import admin
from .models import Course, Enrollment, Program, Section, StudentProfile, Term

admin.site.register([Course, Enrollment, Program, Section, StudentProfile, Term])
