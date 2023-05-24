from django.shortcuts import render
import psycopg2
import psycopg2.extras
import json
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import uuid
from putih.decorators.not_logged_in_decorators import not_login_required
from putih.decorators.logged_in_decorators import *


# Create your views here.

conn = psycopg2.connect(database=settings.DATABASE_NAME, 
                        user=settings.DATABASE_USER, 
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST, 
                        port=settings.DATABASE_PORT, 
                        )

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

#TODO: AYOK TRIAS BIKIN FE
def open(request):
    context = {}
    return render(request, "open.html", context)

@login_required
def dashboard(request):
    query = f"SELECT * FROM NON_PEMAIN INNER JOIN {request.COOKIES.get('role')} ON non_pemain.id=id_{request.COOKIES.get('role')} INNER JOIN STATUS_NON_PEMAIN ON non_pemain.id=id_non_pemain WHERE id = '{request.COOKIES.get('id_role')}'"
    if 'role' in request.COOKIES and 'username' in request.COOKIES:
        cur.execute(query)
        info_user = cur.fetchall()

        info_dashboard=[]

        if (request.COOKIES.get('role') == 'penonton'):

            query=f"""
            select start_datetime, end_datetime, STRING_AGG(nama_tim, ' vs ') as tim_bertanding, s.nama 
            from pembelian_tiket as pt 
            inner join tim_pertandingan as tp on pt.id_pertandingan=tp.id_pertandingan -- add a dot here
            inner join pertandingan as p on tp.id_pertandingan=p.id_pertandingan -- add a dot here
            inner join stadium as s on p.stadium=s.id_stadium -- change stadium to s
            where id_penonton='{request.COOKIES.get('id_role')}'
            group by nomor_receipt, s.id_stadium, p.id_pertandingan
            order by start_datetime
            """
            cur.execute(query)
            info_dashboard = cur.fetchall()
        
        context = {'user' : info_user,
                   'dashboard': info_dashboard}

        print(context)
        
        return render(request, "dashboard.html", context)
    else:
        return HttpResponse("Cookie not found")

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
        status = request.POST.get('status')


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
            cur.execute("INSERT INTO STATUS_NON_PEMAIN VALUES(%s, %s)", [uuid_for_new_non_pemain, status])
            conn.commit()



            return response
        
        
        except Exception as e:
            conn.rollback()
            return HttpResponseBadRequest(e)
        
        finally:
            response = login(request)
            print("dah login")

            return response
            print("dah login")
        
    return HttpResponseNotAllowed("Invalid request method. Please use supported request method.")

@csrf_exempt
@not_login_required
def login(request):
    if (request.method == "POST"):
        print(request.POST)

        username = request.POST.get("username")
        raw_password = request.POST.get("password")


        # response = JsonResponse({"message": "Login successful"})
        # response.set_cookie("username", username, expires=None)

        response = HttpResponseRedirect(reverse('putih:dashboard'))
        response.set_cookie("username", username, expires=None)


        user_as_manajer = check_user_based_on_role(username, raw_password, "MANAJER")
        print(user_as_manajer)
        user_as_penonton = check_user_based_on_role(username, raw_password, "PENONTON")
        user_as_panitia = check_user_based_on_role(username, raw_password, "PANITIA")

        if (user_as_manajer != []):
            response.set_cookie("id_role", user_as_manajer[0]["id_manajer"])
            response.set_cookie("role", "manajer", expires=None)
        elif (user_as_penonton != []):
            response.set_cookie("id_role", user_as_penonton[0]["id_penonton"])
            response.set_cookie("role", "penonton", expires=None)
        elif (user_as_panitia != []):
            response.set_cookie("id_role", user_as_panitia[0]["id_panitia"])
            response.set_cookie("role", "panitia", expires=None)
        else:
            return HttpResponseBadRequest("Invalid credentials")
        
        return response
    
    context = {}
    return render(request, 'open.html', context)



@csrf_exempt
def logout(request):
    response = HttpResponseRedirect(reverse('putih:open'))
    response.delete_cookie('username')
    response.delete_cookie('role')
    response.delete_cookie('id_role')
    if 'id_pertandingan' in request.COOKIES:
        response.delete_cookie('id_pertandingan')
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
