from django.urls import path
from pink.views import index, pinjam_stadium, pinjam_stadium_form, tambah_peminjaman_stadium, mulai_rapat, isi_rapat, \
    process_isi_rapat

app_name = 'pink'

urlpatterns = [
    path('', index, name='index'),
    path('/pinjam_stadium/', pinjam_stadium, name='pinjam_stadium'),
    path('/pinjam_stadium/form/', pinjam_stadium_form, name='pinjam_stadium_form'),
    path('/tambah_peminjaman_stadium/', tambah_peminjaman_stadium, name='tambah_peminjaman_stadium'),
    path('/mulai_rapat/<uuid:pertandingan_id>/', isi_rapat, name='mulai_rapat_id'),
    path('/mulai_rapat/', mulai_rapat, name='mulai_rapat'),
    path('/process_isi_rapat/', process_isi_rapat, name='process_isi_rapat'),
]