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
from putih.views import *
import random


#testing connection in example app
conn = psycopg2.connect(database=settings.DATABASE_NAME, 
                        user=settings.DATABASE_USER, 
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST, 
                        port=settings.DATABASE_PORT, 
                        )

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

def index(request):
    return render(request, 'index.html')

def pembelian_tiket(request):
    query=f"SELECT * FROM STADIUM"
    cur.execute(query)
    info_stadium = cur.fetchall()

    query=f"select min(start_datetime) from pertandingan"
    cur.execute(query)
    tanggal_pertama = cur.fetchall()

    query=f"select max(end_datetime) from pertandingan"
    cur.execute(query)
    tanggal_terakhir = cur.fetchall()
    
    
    context = {'stadiums' : info_stadium, 
               'tanggal_pertama': tanggal_pertama,
               'tanggal_terakhir': tanggal_terakhir}

    


    return render(request, 'pembelian_tiket.html', context)

def pembelian_tiket2(request):
    if (request.method == "POST"):

        id_stadium = request.POST.get("stadium")
        tanggal = request.POST.get("tanggal")
        print(id_stadium)
        print(tanggal)

        # response = HttpResponseRedirect(reverse('krem:pembelian_tiket3'))

        query = f"select * from pertandingan, tim_pertandingan where pertandingan.id_pertandingan=tim_pertandingan.id_pertandingan AND stadium='{id_stadium}' AND start_datetime<='{tanggal}' AND end_datetime>='{tanggal}' order by pertandingan.id_pertandingan"
        cur.execute(query)
        pertandingans = cur.fetchall()
        context = {'pertandingans' : pertandingans}
        return render(request, 'pembelian_tiket2.html', context)
    return render()

def pembelian_tiket3(request):
    if (request.method == "POST"):
        data = json.loads(request.body)
        id_pertandingan = data.get('id_pertandingan')

        response = HttpResponseRedirect(reverse('krem:pembelian_tiket3'))
        response['location'] = reverse('krem:pembelian_tiket3')
        response.set_cookie("id_pertandingan", id_pertandingan)
        print(response)
        return response
    if (request.method == "GET"):
        print('masuk get')
        id_pertandingan = request.COOKIES.get('id_pertandingan')
        print(request.COOKIES.get('id_pertandingan'))
        
        return render(request, 'pembelian_tiket3.html', context={})

def pembelian_tiket4(request):
    if(request.method == "POST"):

        id_penonton = request.COOKIES.get('id_role')
        id_pertandingan = request.COOKIES.get('id_pertandingan')
        jenis_tiket = request.POST.get('jenis_tiket')
        jenis_pembayaran = request.POST.get('jenis_pembayaran')
        nomor_receipt = generate_random_receipt()

        string = f"'{id_penonton}', '{id_pertandingan}', '{jenis_tiket}', '{jenis_pembayaran}', '{nomor_receipt}'"
        print(string)

        query = f"INSERT INTO PEMBELIAN_TIKET VALUES('{nomor_receipt}', '{id_penonton}', '{jenis_tiket}', '{jenis_pembayaran}', '{id_pertandingan}')"
        cur.execute(query)
        conn.commit()

        
        response = HttpResponseRedirect(reverse('putih:dashboard'))
        return response

    return 

def generate_random_receipt():
    random_numbers = [random.randint(1000, 9999) for _ in range(4)]
    random_string = '-'.join(map(str, random_numbers))
    return random_string


#test
def ex_query(request):
    cur.execute('select * from test')
    res = cur.fetchall()
    return HttpResponse(res)