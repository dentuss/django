from django.contrib import admin
from .models import StudentScore, DisciplineExam


@admin.register(StudentScore)
class StudentScoreAdmin(admin.ModelAdmin):
    list_display = ("surname", "score")


@admin.register(DisciplineExam)
class DisciplineExamAdmin(admin.ModelAdmin):
    list_display = ("title", "exam_date")
