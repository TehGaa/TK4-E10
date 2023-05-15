from django.urls import path
from example_app.views import index, ex_query

app_name = 'example_app'

urlpatterns = [
    path('', index, name='index'),
    path('ex_query', ex_query, name='ex_query')
]