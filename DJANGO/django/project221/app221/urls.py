from django.urls import path
from . import views


# КОНСПЕКТ: urls.py приложения app221 — маршруты ("роуты") URL -> view
#
# Файл подключается в основном project221/urls.py через include('app221.urls')
# path(route, view, name) связывает URL с функцией из views.py. Параметр name
# нужен, чтобы в шаблонах и в коде ссылаться на маршрут по имени (например,
# в register-view используется redirect('register') — идёт сюда по name)
#
# Здесь живут все 5 страниц проекта:
#   ""          -> главная (ДЗ: Layouting, index.html)
#   "intro/"    -> ДЗ: Вступ до Django (страница установки + время загрузки)
#   "hello/"    -> простая проверочная функция
#   "privacy/"  -> ДЗ: Layouting, страница "Політика конфіденційності"
#   "register/" -> ДЗ: Параметри запитів. Форми + Валідація форм + Моделі

urlpatterns = [
    path('', views.index, name="index"),
    path('intro/', views.intro, name="intro"),
    path('hello/', views.hello, name="hello"),
    path('privacy/', views.privacy, name="privacy"),
    path('register/', views.register, name="register"),
]
