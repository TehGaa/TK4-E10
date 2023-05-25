from hijau.views import *
from django.urls import path

app_name = "hijau"

urlpatterns = [
    path('', home, name="home"),
    path('create-tim', create_tim, name='create_tim'),
    path('update-captain', update_captain, name='update-captain'),
    path('delete-pemain', delete_pemain, name='delete-pemain'),
    path('add-pemain', add_pemain, name='add-pemain'),
    
]