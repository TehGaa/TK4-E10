#url routing
from putih.views import *
from django.urls import path


app_name = 'putih'

urlpatterns = [
    path('', dashboard, name='dashboard'),
    path('login', login, name='login'),
    path('register', register, name='register'),
    path('logout', logout, name='logout'),
]