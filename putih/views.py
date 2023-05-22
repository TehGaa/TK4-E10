from django.shortcuts import render
import psycopg2
import psycopg2.extras
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseRedirect
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import uuid
from putih.decorators.not_logged_in_decorators import not_login_required


# Create your views here.

conn = psycopg2.connect(database=settings.DATABASE_NAME, 
                        user=settings.DATABASE_USER, 
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST, 
                        port=settings.DATABASE_PORT, 
                        )

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#TODO: AYOK TRIAS BIKIN FE
def dashboard(request):
    context = {}
    return render(request, "open.html", context)

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
        jabatan = request.POST.get('jabatan')


        response = HttpResponse()
        response.status_code = 200
        response.content = "Register Success"

        try:
            psycopg2.extras.register_uuid()

            uuid_for_new_non_pemain = generate_uuid()

            cur.execute("INSERT INTO USER_SYSTEM VALUES(%s, %s)", [username, raw_password,])
            cur.execute("INSERT INTO NON_PEMAIN VALUES(%s, %s, %s, %s, %s, %s)",
                        [uuid_for_new_non_pemain, nama_depan, nama_belakang, nomor_hp, email, alamat])
            create_user_based_on_role(username,
                                      uuid_for_new_non_pemain,
                                      role,
                                      jabatan)
            conn.commit()
            return response
        
        except Exception as e:
            conn.rollback()
            return HttpResponseBadRequest(e)
        
    return HttpResponseNotAllowed("Invalid request method. Please use supported request method.")

@csrf_exempt
@not_login_required
def login(request):
    if (request.method == "POST"):
        username = request.POST.get("username")
        raw_password = request.POST.get("password")

        response = HttpResponse()
        response.status_code = 200
        response.set_cookie("username", username, expires=None)
        response.content = "Login Success"

        user_as_manajer = check_user_based_on_role(username, raw_password, "MANAJER")
        user_as_penonton = check_user_based_on_role(username, raw_password, "PENONTON")
        user_as_panitia = check_user_based_on_role(username, raw_password, "PANITIA")

        if (user_as_manajer != []):
            response.set_cookie("id_role", user_as_manajer[0]["id_manajer"])
            response.set_cookie("role", "manajer", expires=None)
        elif (user_as_penonton != []):
            response.set_cookie("id_role", user_as_manajer[0]["id_penonton"])
            response.set_cookie("role", "penonton", expires=None)
        elif (user_as_panitia != []):
            response.set_cookie("id_role", user_as_manajer[0]["id_panitia"])
            response.set_cookie("role", "panitia", expires=None)
        else:
            return HttpResponseBadRequest("Invalid credentials")
        
        return response
    
    context = {}
        
    return render(request, 'login.html', context)

@csrf_exempt
def logout(request):
    response = HttpResponseRedirect(reverse('putih:dashboard'))
    response.delete_cookie('username')
    response.delete_cookie('role')
    response.delete_cookie('id_role')
    return response

def check_user_based_on_role(username, password, role):
    query = f"SELECT * FROM USER_SYSTEM NATURAL JOIN {role} WHERE username = '{username}' AND password = '{password}'"
    cur.execute(query)
    get_user_from_database = cur.fetchall()
    json_format(get_user_from_database)
    return get_user_from_database

def create_user_based_on_role(username, generated_uuid, role, jabatan=None):

    query = f"INSERT INTO {str(role).upper()}"
    if (str(role).upper() == "PANITIA"):
        cur.execute(query+" VALUES(%s, %s, %s)", [generated_uuid, jabatan, username,])
    else:
        cur.execute(query+" VALUES(%s, %s)", [generated_uuid, username,])
    conn.commit()

def generate_uuid():

    while (True):
        generated_uuid = uuid.uuid4()
        cur.execute("SELECT * FROM NON_PEMAIN WHERE id = %s", (generated_uuid,))
        lst_non_pemain = cur.fetchall()
        if (lst_non_pemain == []):
            return generated_uuid

def json_format(lst):
    for i in range(len(lst)):
        lst[i] = dict(lst[i])
