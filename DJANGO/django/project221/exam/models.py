from django.db import models


class StudentScore(models.Model):
    surname = models.CharField(max_length=120)
    score = models.PositiveSmallIntegerField()

    def __str__(self):
        return f"{self.surname} ({self.score})"


class DisciplineExam(models.Model):
    title = models.CharField(max_length=180)
    exam_date = models.DateField()

    def __str__(self):
        return f"{self.title} — {self.exam_date}"
