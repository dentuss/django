from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="index"),
    path('intro/', views.intro, name="intro"),
    path('hello/', views.hello, name="hello"),
    path('privacy/', views.privacy, name="privacy"),
    path('register/', views.register, name="register"),
]
