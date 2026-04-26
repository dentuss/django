from django.urls import path
from . import views


urlpatterns = [
    path('', views.exam_home, name='exam_home'),
    path('score100/', views.score_100_form, name='exam_score100'),
    path('grade4/', views.grade_choice_form, name='exam_grade4'),
    path('discipline/', views.discipline_form, name='exam_discipline'),
]
