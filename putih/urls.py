#url routing
from putih.views import *
from django.urls import path


app_name = 'putih'

urlpatterns = [
    path('login', login, name='login'),
]