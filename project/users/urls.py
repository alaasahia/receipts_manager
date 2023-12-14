from os import name
from django.core.checks import register
from django.urls import path
from .views import user_logout, user_register, user_login

urlpatterns = [
    path('register/', user_register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout')
]
