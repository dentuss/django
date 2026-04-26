from django.shortcuts import render
from .forms import Score100Form, GradeChoiceForm, DisciplineExamDateForm


def exam_home(request):
    # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
    # Изменение: добавлена страница /exam как отдельная точка входа учебного модуля
    # Зачем: выполнить задание о новой странице в Django-проекте
    return render(request, "exam/home.html")


def score_100_form(request):
    form = Score100Form(request.POST or None)
    return render(request, "exam/score_100.html", {"form": form})


def grade_choice_form(request):
    form = GradeChoiceForm(request.POST or None)
    return render(request, "exam/grade_choice.html", {"form": form})


def discipline_form(request):
    form = DisciplineExamDateForm(request.POST or None)
    return render(request, "exam/discipline.html", {"form": form})
