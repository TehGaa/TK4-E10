from django.shortcuts import render
import psycopg2
import psycopg2.extras
import json
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import uuid

# Create your views here.
conn = psycopg2.connect(database=settings.DATABASE_NAME,
                        user=settings.DATABASE_USER,
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST,
                        port=settings.DATABASE_PORT,
                        )

cur = conn.cursor()

def index(request):
    query = f"SELECT * FROM STADIUM"
    cur.execute(query)
    res = cur.fetchall()
    print(res)
    return render(request, 'index.html')