from django.shortcuts import render
import psycopg2
from django.http import HttpResponse
from django.conf import settings



#testing connection in example app
conn = psycopg2.connect(database=settings.DATABASE_NAME, 
                        user=settings.DATABASE_USER, 
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST, 
                        port=settings.DATABASE_PORT, 
                        )

cur = conn.cursor()

def index(request):
    return render(request, 'index.html')

#test
def ex_query(request):
    cur.execute('select * from test')
    res = cur.fetchall()
    return HttpResponse(res)