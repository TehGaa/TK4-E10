#url routing
from putih.views import *
from django.urls import path
from django.contrib.auth import views as auth_views



app_name = 'putih'

urlpatterns = [
    path('', login, name='open'),
    path('dashboard', dashboard, name='dashboard'),
    path('login', login, name='login'),
    path('login.php', login, name='loginphp'),
    path('register', register, name='register'),
    path('register.php', register, name='register.php'),
    path('logout', logout, name='logout'),
]