from django.urls import path

from krem.views import index

app_name = "donation"

urlpatterns = [
    path('', index, name="index"),
]