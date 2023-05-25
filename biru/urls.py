#url routing
from biru.views import *
from django.urls import path

app_name = 'biru'

urlpatterns = [
    path('data_list_pertandingan', data_list_pertandingan, name='data_list_pertandingan'),
    path('dropdown_stadium', dropdown_stadium, name='dropdown_stadium'),
    path('data_list_waktu', data_list_waktu, name='data_list_waktu'),
    path('create_pertandingan', create_pertandingan, name='create_pertandingan'),
    path('delete', delete_pertandingan, name="delete_pertandingan"),
    path('submit_create_pertandingan', submit_create_pertandingan, name='submit_create_pertandingan'),
    path('update_dropdown_stadium', update_dropdown_stadium, name='update_dropdown_stadium'),
    path('update_create_pertandingan', update_create_pertandingan, name='update_create_pertandingan'),
    path('update_submit_create_pertandingan', update_submit_create_pertandingan, name='update_submit_create_pertandingan'),
]