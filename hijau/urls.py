from hijau.views import *
from django.urls import path

app_name = "hijau"

urlpatterns = [
    path('', home, name="home"),
    path('create-tim', create_tim, name='create-tim'),
    path('update-captain', update_captain, name='update-captain'),
    path('delete-pemain', delete_pemain, name='delete-pemain'),
    path('add-pemain', add_pemain, name='add-pemain'),
    path('add-pelatih', add_pelatih, name='add-pelatih'),
    path('insert-pelatih', insert_pelatih, name='insert-pelatih-into-tim'),
    path('insert-pemain-into-tim', insert_pemain_into_tim, name='insert-pemain-into-tim'),
    path('update-pelatih', update_pelatih, name='update-pelatih'),
]   