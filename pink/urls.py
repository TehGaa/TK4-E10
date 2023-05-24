from django.urls import path
from pink.views import index

app_name = 'pink'

urlpatterns = [
    path('', index, name='index'),
]