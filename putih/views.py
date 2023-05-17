from django.shortcuts import render
import psycopg2
import psycopg2.extras
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
import json
import uuid


# Create your views here.

conn = psycopg2.connect(database=settings.DATABASE_NAME, 
                        user=settings.DATABASE_USER, 
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST, 
                        port=settings.DATABASE_PORT, 
                        )

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

@csrf_exempt
def register(request):
    if (request.method == "POST"):
        nama_depan = request.POST.get("nama_depan")
        nama_belakang = request.POST.get("nama_belakang")
        nomor_hp = request.POST.get("nomor_hp")
        email = request.POST.get("email")
        alamat = request.POST.get("alamat")
        username = request.POST.get("username")
        raw_password = request.POST.get("password")
        role = request.POST.get('role')

        response = HttpResponse()
        response.status_code = 200
        response.content = "Register Success"

        check_user_exists_as_manajer = check_username_exists_as_manajer(username)
        check_user_exists_as_penonton = check_username_exists_as_penonton(username)
        check_user_exists_as_panitia = check_username_exists_as_panitia(username)

        if (check_user_exists_as_manajer or
            check_user_exists_as_penonton or
            check_user_exists_as_panitia):
            return HttpResponseBadRequest("User already exist")
        else:
            # create_user_based_on_role(username, raw_password, role)
            return response
        
    return HttpResponseNotAllowed("Invalid request method. Please use supported request method.")

@csrf_exempt
def login(request):
    if (request.method == "POST"):
        username = request.POST.get("username")
        raw_password = request.POST.get("password")

        response = HttpResponse()
        response.status_code = 200
        response.set_cookie("username", username, expires=None)
        response.content = "Login Success"

        if (check_user_is_manajer(username, raw_password) != []):
            response.set_cookie("role", "manajer", expires=None)
        elif (check_user_is_penonton(username, raw_password) != []):
            response.set_cookie("role", "penonton", expires=None)
        elif (check_user_is_panitia(username, raw_password) != []):
            response.set_cookie("role", "panitia", expires=None)
        else:
            return HttpResponseBadRequest("Invalid credentials")
        
        return response
        
    return HttpResponseNotAllowed("Invalid request method. Please use supported request method.")

@csrf_exempt
def logout(request):
    pass


def check_user_is_manajer(username, password):
    query = "SELECT * FROM USER_SYSTEM NATURAL JOIN MANAJER WHERE username = '" + username + "'"+\
            " AND password = '" + password + "'"
    cur.execute(query)
    get_manajer_from_database = cur.fetchall()
    json_format(get_manajer_from_database)
    return get_manajer_from_database

def check_user_is_penonton(username, password):
    query = "SELECT * FROM USER_SYSTEM NATURAL JOIN PENONTON WHERE username = '" + username + "'"+\
            " AND password = '" + password + "'"
    cur.execute(query)
    get_penonton_from_database = cur.fetchall()
    json_format(get_penonton_from_database)
    return get_penonton_from_database

def check_user_is_panitia(username, password):
    query = "SELECT * FROM USER_SYSTEM NATURAL JOIN PANITIA WHERE username = '" + username + "'"+\
            " AND password = '" + password + "'"
    cur.execute(query)
    get_panitia_from_database = cur.fetchall()
    json_format(get_panitia_from_database)
    return get_panitia_from_database

def check_username_exists_as_manajer(username):
    query = "SELECT * FROM USER_SYSTEM NATURAL JOIN MANAJER WHERE username = '" + username + "'"
    cur.execute(query)
    get_manajer_from_database = cur.fetchall()
    json_format(get_manajer_from_database)
    return get_manajer_from_database != []

def check_username_exists_as_penonton(username):
    query = "SELECT * FROM USER_SYSTEM NATURAL JOIN PENONTON WHERE username = '" + username + "'"
    cur.execute(query)
    get_penonton_from_database = cur.fetchall()
    json_format(get_penonton_from_database)
    return get_penonton_from_database != []

def check_username_exists_as_panitia(username):
    query = "SELECT * FROM USER_SYSTEM NATURAL JOIN PANITIA WHERE username = '" + username + "'"
    cur.execute(query)
    get_panitia_from_database = cur.fetchall()
    json_format(get_panitia_from_database)
    return get_panitia_from_database != []

#MASIH ERROR
def create_user_based_on_role(username, password, role):
    uuid_for_user = generate_uuid(role)

    query_insert_user_system = "INSERT INTO USER_SYSTEM VALUES('" + username + "', '" + password +"')"
    cur.execute(query_insert_user_system)
    conn.commit()

    query_insert_user_role_based = "INSERT INTO " + str(role).upper() + " VALUES('" + uuid_for_user + "', '" + username +"')"
    cur.execute(query_insert_user_role_based)
    conn.commit()

def generate_uuid(role):
    while (True):
        generated_uuid = str(uuid.uuid4())
        query_get_all_non_pemain = "SELECT * FROM NON_PEMAIN WHERE id_"+ role +" = '" + generated_uuid + "'"
        cur.execute(query_get_all_non_pemain)
        lst_non_pemain = cur.fetchall()
        if (lst_non_pemain == []):

            return generated_uuid


def generate_uuid_for_penonton():
    pass

def json_format(lst):
    for i in range(len(lst)):
        lst[i] = dict(lst[i])
