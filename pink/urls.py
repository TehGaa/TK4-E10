from django.urls import path
from pink.views import index, pinjam_stadium, pinjam_stadium_form

app_name = 'pink'

urlpatterns = [
    path('', index, name='index'),
    path('/pinjam_stadium/', pinjam_stadium, name='pinjam_stadium'),
    path('/pinjam_stadium/form/', pinjam_stadium_form, name='pinjam_stadium_form'),
]