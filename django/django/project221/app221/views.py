from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
from datetime import datetime
from .forms import RegistrationForm
from django.shortcuts import render, redirect
from django.contrib import messages

# =============================================================================
# КОНСПЕКТ: views.py — "вьюхи" (view-функции) Django.
#
# В Django архитектура MVT (Model-View-Template):
#   * Модель — описание данных в БД (models.py)
#   * View — функция/класс, который принимает HttpRequest и возвращает HttpResponse
#   * Template — HTML-шаблон, рендерится с контекстом
#
# urls.py связывает URL с конкретной view-функцией. Ниже реализованы 5 вьюх:
# hello (простой текст), index (главная), intro (страница установки Django),
# privacy (политика конфиденциальности), register (форма регистрации).
# =============================================================================

def hello(request):
    # Простейший вариант: просто возвращаем текст. Без шаблона, без контекста.
    # Полезно для проверки, что сервер жив (GET /hello/).
    return HttpResponse("Hello World!")


def index(request):
    # Главная страница. Грузим шаблон через loader.get_template и рендерим его
    # с контекстом (словарь переменных, доступных в шаблоне).
    # В index.html выводятся {{ x }} и {{ str }}.
    template = loader.get_template('index.html')
    context = {
        'x': 10,
        'str': 'the string'
    }
    return HttpResponse(template.render(context, request))


# -----------------------------------------------------------------------------
# ДЗ: Вступ до Django
# Задание: Реалізувати окрему сторінку Intro. На ній вивести дані про
#          встановлення та налаштування фреймворка Django. А також вивести
#          дані про час завантаження сторіки: "Сторінка завантажена о 14:43 13.03.2026".
#          На головній сторінці розмістити посилання на неї. Додати скріншоти.
#
# Что сделано:
#   1. View intro() ниже — готовит timestamp в нужном формате "%H:%M %d.%m.%Y"
#      и прокидывает его в шаблон intro.html как load_time.
#   2. Шаблон intro.html содержит инструкции по установке Django
#      (venv, activate, pip install, startproject) и выводит {{ load_time }}.
#   3. В index.html есть ссылка <a href="intro">Intro page</a>.
#   4. Скриншоты лежат в django/RESULT/ (hw-*.png).
# -----------------------------------------------------------------------------
def intro(request):
    now = datetime.now()
    # Формат ровно такой, как в задании: "14:43 13.03.2026".
    timestamp = now.strftime("%H:%M %d.%m.%Y")
    context = {
        'load_time': timestamp
    }
    template = loader.get_template('intro.html')
    return HttpResponse(template.render(context, request))


# -----------------------------------------------------------------------------
# ДЗ: Layouting
# Задание: Реалізувати усі сторінки проєкту у шаблонному стилі. Створити
#          сторінку "Політика конфіденційності" (Privacy) і наповнити її контентом.
#
# Что сделано:
#   * layout.html — общий макет с navbar (ссылки: Главная, Privacy, Register),
#     контейнером main, блоком messages и footer. Остальные шаблоны
#     extends "layout.html" и переопределяют блоки title / render_body.
#   * privacy.html — отдельная страница "Політика конфіденційності" с
#     контентом о сборе данных, их использовании, защите и пр.
#   * view privacy() ниже просто рендерит этот шаблон.
# -----------------------------------------------------------------------------
def privacy(request):
    template = loader.get_template('privacy.html')
    return HttpResponse(template.render({}, request))


# -----------------------------------------------------------------------------
# ДЗ: Параметри запитів. Форми
# Задание: Створити форму Django з різноманітними типами полів введення
#          (текстові, числові, дата, чекбокси, радіо тощо). Приклад — реєстрація
#          користувача. Описати необхідні класи та поля.
#
# ДЗ: Валідація форм
# Задание: Забезпечити валідацію форми реєстрації та відображення її
#          результатів зі стилізацією.
#
# ДЗ: Моделі
# Задание: Реалізувати на сторінці форм виведення повідомлення про успішну
#          реєстрацію нового користувача.
#
# Что сделано в view register() ниже:
#   1. GET-запрос -> показываем пустую форму RegistrationForm() (см. forms.py).
#   2. POST-запрос -> создаём форму с данными (request.POST), вызываем
#      form.is_valid() — это запускает все валидаторы в forms.py
#      (clean_username, clean_age, clean — совпадение паролей).
#   3. Если форма валидна — через django.contrib.messages добавляем flash-
#      сообщение "Акаунт створено" (ДЗ: Моделі). messages.success кладёт
#      сообщение в сессию, и в layout.html оно выводится в красивой плашке
#      alert-success. Затем redirect('register') — POST/Redirect/GET паттерн,
#      чтобы обновление страницы не отправляло форму заново.
#   4. Если форма невалидна — возвращаем тот же шаблон register.html.
#      Внутри шаблона для каждого поля показываются ошибки и подсвечивается
#      стиль invalid-feedback / is-invalid (ДЗ: Валідація форм).
#
# Скриншоты — в http/result/ и django/RESULT/.
# -----------------------------------------------------------------------------
def register(request):
    if request.method == 'POST':
        # Форма, заполненная пользователем.
        form = RegistrationForm(request.POST)
        if form.is_valid():
            # cleaned_data — данные после всех валидаторов (чистые и типизированные).
            username = form.cleaned_data.get('username')
            # messages.success — механизм одноразовых уведомлений Django.
            # Чтобы оно появилось, в settings.py подключен MessageMiddleware.
            messages.success(request, f'Акаунт для {username} успішно створено! Тепер ви можете увійти.')
            # Паттерн POST -> Redirect -> GET: избегает повторной отправки формы
            # при обновлении страницы в браузере.
            return redirect('register')
    else:
        # GET: отдаём пустую форму.
        form = RegistrationForm()

    # render() — короткий путь: сам собирает HttpResponse из шаблона+контекста.
    return render(request, 'register.html', {'form': form})
