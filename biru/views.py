from django.shortcuts import render
import psycopg2
import psycopg2.extras
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.urls import reverse
from putih.decorators.logged_in_decorators import login_required_as_role
from django.shortcuts import redirect, render
from django.http import JsonResponse, QueryDict, HttpResponse
from django.core import serializers
from django.db import connection
from django.db.models.functions import datetime


# Create your views here.
conn = psycopg2.connect(database=settings.DATABASE_NAME, 
                        user=settings.DATABASE_USER, 
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST, 
                        port=settings.DATABASE_PORT, 
                        )

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

# @login_required_as_role('manajer')
# def home(request):
#     if (request.method == 'POST'):
#         nama_tim = request.POST.get('nama-tim')
#         nama_univ = request.POST.get('nama-univ')
        
#         cur.execute("SELECT * FROM TIM WHERE nama_tim = %s AND nama_univ = %s", [nama_tim, nama_univ, ])
#         is_registered = cur.fetchall() == []
        
#         if (is_registered):
#             return f"Not Registered"
        
#         response = HttpResponseRedirect(reverse('hijau:show_tim'))
        
#         return 
#     return render(request, 'mengelola_tim.html')

# @login_required_as_role('manajer')
# def create_tim(request):
#     if (request.method == "POST"):
#         nama_tim = request.POST.get('nama-tim')
#         nama_univ = request.POST.get('nama_univ')
#         try:
#             cur.execute('INSERT INTO TIM VALUES(%s, %s)', [nama_tim, nama_univ, ])
#             conn.commit()
#             return f'insert tim {nama_tim} with univ name {nama_univ} succeded'
#         except Exception as e:
#             conn.rollback()
#             return HttpResponse(e)
    
#     return HttpResponseNotAllowed("Invalid request method. Please use supported request method.")

# @login_required_as_role('manajer')
# def show_tim(request):
#     pass

def fetch(cursor):
    columns = [col[0] for col in cursor.description]
    return [dict(zip(columns, row)) for row in cursor.fetchall()]

def is_logged(request):
    try:
        request.session['email']
        return True
    except KeyError:
        return False

def data_list_pertandingan(request):
    # if request.method == 'GET' and is_logged(request):
    #     if request.session['is_admin_satgas']:
            query = """
                SELECT DISTINCT ON (B.id_pertandingan) B.id_pertandingan, A.nama_tim AS nama_tim_a, B.nama_tim AS nama_tim_b
                FROM tim_pertandingan AS A, tim_pertandingan AS B
                WHERE A.id_pertandingan = B.id_pertandingan AND A.nama_tim!=b.nama_tim;
            """
            
            # cursor = connection.cursor()
            cur.execute(query)
            data = fetch(cur)

            grup_a = data[:8]
            grup_b = data[8:16]

            response = {'data': data, 'data_1': grup_a, 'data_2': grup_b}
            print(response)
            return render(request, 'data_list_pertandingan.html', response)
        # return JsonResponse({'not_allowed': True})
    # return redirect("/authenticate/?next=/jadwal-faskes/")

def data_list_waktu(request):
            query = """
                SELECT DISTINCT ON (B.id_pertandingan) B.id_pertandingan, A.nama_tim AS nama_tim_a, B.nama_tim AS nama_tim_b
                FROM tim_pertandingan AS A, tim_pertandingan AS B
                WHERE A.id_pertandingan = B.id_pertandingan AND A.nama_tim!=b.nama_tim;
            """
            cur.execute(query)
            data = fetch(cur)

            grup_a = data[:8]
            grup_b = data[8:16]

            response = {'data': data, 'data_1': grup_a, 'data_2': grup_b}
            print(response)
            return render(request, 'data_list_waktu.html', response)

def dropdown_stadium(request):
            query = """
                SELECT S.Nama
                FROM Stadium AS S;
            """

            cur.execute(query)
            data = fetch(cur)
            response = {'data': data}
            print(response)
            
            return render(request, 'dropdown_stadium.html', response)

def dropdown_stadium2(request):
            if request.method == 'POST':
                tanggal = request.POST.get('tanggal')
                    
                query = """
                    SELECT S.Nama
                    FROM Stadium AS S
                    WHERE S.ID_Stadium NOT IN (
                        SELECT P.Stadium
                        FROM Pertandingan AS P
                        WHERE DATE %s BETWEEN P.Start_Datetime::date AND P.End_Datetime::date;
                    )
                """
                cur.execute(query, [tanggal])
                data = fetch(cur)

                response = {'data': data}
                return render(request, 'dropdown_stadium.html', response)
            else:
                return render(request, 'dropdown_stadium.html')

def pembuatanPertandingan(request):
    if request.method == 'POST':
        tanggal = request.POST.get('tanggal')

        with connection.cursor() as cursor:
            query = """
                SELECT S.Nama
                FROM Stadium AS S
                WHERE S.ID_Stadium NOT IN (
                    SELECT P.Stadium
                    FROM Pertandingan AS P
                    WHERE DATE %s BETWEEN P.Start_Datetime::date AND P.End_Datetime::date
                )
            """
            cursor.execute(query, [tanggal])
            stadiums = [row[0] for row in cursor.fetchall()]

        context = {'stadiums': stadiums}
        return render(request, 'pembuatanPertandingan.html', context)
    else:
        return render(request, 'pembuatanPertandingan.html')

def create_pertandingan(request):
            query_wasit = """
                SELECT nama_depan||' '||nama_belakang as nama, w.id_wasit
                FROM wasit as w, non_pemain
                WHERE NON_PEMAIN.id = w.id_wasit;
            """
            query_tim = """
                SELECT T.nama_tim
                FROM tim as t;
            """
            cur.execute(query_wasit)
            data_w = fetch(cur)

            cur.execute(query_tim)
            data_t = fetch(cur)

            response = {'data_w': data_w, 'data_t': data_t}
            print(response)
            return render(request, 'create_pertandingan.html', response)


# II KSAK LITAAAAAAAAAA

def delete_pertandingan(request):
	delete_tim_pertandingan(request.POST)
	return redirect("biru:data_list_pertandingan")

def delete_tim_pertandingan(data):
    query = f"""
    DELETE FROM tim_pertandingan
    WHERE id_pertandingan = '{data['id_pertandingan']}';
    """
    cur.execute(query)

# INI MAU COBA UPDATEEEEEEEEE


