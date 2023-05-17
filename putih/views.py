from django.shortcuts import render
import psycopg2
import psycopg2.extras
from django.http import HttpResponse, HttpResponseNotAllowed
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt


# Create your views here.

conn = psycopg2.connect(database=settings.DATABASE_NAME, 
                        user=settings.DATABASE_USER, 
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST, 
                        port=settings.DATABASE_PORT, 
                        )

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)


@csrf_exempt
def login(request):
    if (request.method == "POST"):
        username = request.POST.get("username")
        print(username)
        raw_password = request.POST.get("password")
        print(raw_password)
        return HttpResponse(check_user_is_manajer(str(username)))

        
    return HttpResponseNotAllowed("Invalid request method. Please use supported request method.")


def check_user_is_manajer(username):
    query = format("SELECT * FROM USER_SYSTEM NATURAL JOIN MANAJER WHERE username = %s", username)
    cur.execute(query)
    get_manajer_from_database = cur.fetchall()
    return get_manajer_from_database

def check_user_is_penonton(username):
    query = format("SELECT * FROM USER_SYSTEM NATURAL JOIN PENONTON WHERE username = %s", username)
    cur.execute(query)
    get_penonton_from_database = cur.fetchall()
    return get_penonton_from_database

def check_user_is_panitia(username):
    query = format("SELECT * FROM USER_SYSTEM NATURAL JOIN PANITIA WHERE username = %s", username)
    cur.execute(query)
    get_panitia_from_database = cur.fetchall()
    return get_panitia_from_database

