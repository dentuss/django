from django import forms


class Score100Form(forms.Form):
    surname = forms.CharField(label="Прізвище", max_length=100)
    score = forms.IntegerField(label="Оцінка (0-100)", min_value=0, max_value=100)


class GradeChoiceForm(forms.Form):
    grade_choices = [
        ("excellent", "Відмінно"),
        ("good", "Добре"),
        ("satisfactory", "Задовільно"),
        ("unsatisfactory", "Незадовільно"),
    ]
    surname = forms.CharField(label="Прізвище", max_length=100)
    grade = forms.ChoiceField(label="Оцінка", choices=grade_choices)


class DisciplineExamDateForm(forms.Form):
    discipline = forms.CharField(label="Навчальна дисципліна", max_length=150)
    exam_date = forms.DateField(label="Дата екзамену", widget=forms.DateInput(attrs={"type": "date"}))
