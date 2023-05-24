from django.urls import path

from krem.views import *

app_name = "krem"

urlpatterns = [
    path('', index, name="index"),
    path('pembelian_tiket', pembelian_tiket, name="pembelian_tiket"),
    path('pembelian_tiket2', pembelian_tiket2, name="pembelian_tiket2"),
    path('pembelian_tiket3', pembelian_tiket3, name="pembelian_tiket3"),
    path('pembelian_tiket4', pembelian_tiket4, name="pembelian_tiket4"),
]