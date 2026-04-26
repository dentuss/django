from django import forms
from django.core.exceptions import ValidationError

# КОНСПЕКТ: forms.py — формы Django
#
# forms.Form — класс-обёртка над HTML-формой. Основные плюсы:
#   - автоматически генерирует HTML-инпуты (<input>, <select>, ...);
#   - берёт на себя валидацию (типы данных, обязательность, длина);
#   - даёт удобный хук для кастомной валидации: методы clean_<field> и clean()
#
# После form.is_valid() данные доступны в form.cleaned_data (уже "чистые":
# строки превращены в int/date/..., пустые значения нормализованы и т.д.)




# ДЗ: Параметри запитів. Форми
# Задание: Создать форму Django с различными типами полей: текстовые,
#          числовые, дата, чекбоксы, радио. Пример — регистрация
#
# ДЗ: Валідація форм
# Задание: Обеспечить валидацию формы регистрации и отображение результатов
#          со стилизацией
#
# Что сделано:
#   Класс RegistrationForm ниже содержит поля разных типов:
#     - username — CharField + TextInput (текстовое поле) с min_length=4
#     - password — CharField + PasswordInput (поле пароля)
#     - confirm_password — CharField + PasswordInput (подтверждение)
#     - age — IntegerField + NumberInput (числовое поле)
#   У всех полей через widget=... заданы CSS-классы Bootstrap и плейсхолдеры
#
#   Валидация реализована тремя способами (все три варианта Django):
#     1) clean_username — валидатор одного поля (запрещает слово "admin");
#     2) clean_age — валидатор одного поля (требует возраст >= 18);
#     3) clean — валидатор всей формы (проверяет совпадение паролей)

class RegistrationForm(forms.Form):
    # Текстовое поле
    username = forms.CharField(
        label="Логін",
        # min_length=4 — встроенная валидация Django: если короче, будет ошибка
        # "Ensure this value has at least 4 characters"
        min_length=4,
        # widget задаёт, как поле выглядит в HTML. TextInput -> <input type="text">
        # attrs передаются как HTML-атрибуты (класс Bootstrap + placeholder)
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Мінімум 4 символи'})
    )

    # Поле пароля
    password = forms.CharField(
        label="Пароль",
        # PasswordInput -> <input type="password">: маскирует ввод точками
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Придумайте складний пароль'})
    )

    # Поле подтверждения пароля
    # Проверяется в методе clean() (см. ниже) на совпадение с password
    confirm_password = forms.CharField(
        label="Підтвердіть пароль",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    # Числовое поле
    age = forms.IntegerField(
        label="Вік",
        # NumberInput -> <input type="number">, браузер сам покажет стрелочки-спиннер
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    # Валідація окремого поля (username)
    # Django автоматически вызывает все методы вида clean_<имя_поля>
    # Если вернуть значение — оно попадёт в cleaned_data. Если кинуть
    # ValidationError — появится ошибка в form.errors["username"]
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if "admin" in username.lower():
            raise ValidationError("Логін не може містити слово 'admin'.")
        return username

    # Валідація віку — запрещаем регистрацию до 18
    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age < 18:
            raise ValidationError("Реєстрація дозволена лише особам від 18 років.")
        return age

    # Валідація всієї форми (співпадіння паролів)
    # clean() вызывается ПОСЛЕ всех clean_<field>, поэтому здесь мы знаем,
    # что отдельные поля уже прошли валидацию
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # add_error добавляет ошибку конкретному полю — тогда в шаблоне
        # она отрисуется рядом с этим полем (а не в non_field_errors)
        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Паролі не співпадають!")
