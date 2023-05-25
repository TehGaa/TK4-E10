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

        query = f"INSERT INTO PEMBELIAN_TIKET VALUES('{nomor_receipt}', '{id_penonton}', '{jenis_tiket}', '{jenis_pembayaran}', '{id_pertandingan}')"
        cur.execute(query)
        conn.commit()

        
        response = HttpResponseRedirect(reverse('putih:dashboard'))
        return response

    return 

def list_pertandingan_penonton(request):

    query=f"""
            select start_datetime, end_datetime, STRING_AGG(nama_tim, ' vs ') as tim_bertanding, s.nama 
            from tim_pertandingan as tp 
            inner join pertandingan as p on tp.id_pertandingan=p.id_pertandingan -- add a dot here
            inner join stadium as s on p.stadium=s.id_stadium -- change stadium to s
            group by s.id_stadium, p.id_pertandingan
            order by start_datetime
            """
    cur.execute(query)
    list_pertandingan = cur.fetchall()
    context = {'pertandingans' : list_pertandingan}

    return render(request, 'list_pertandingan_penonton.html', context)


def list_pertandingan_manajer(request):
    id_manajer = request.COOKIES.get('id_role')

    query=f"""select p.id_pertandingan, start_datetime, end_datetime, STRING_AGG(nama_tim, ' vs ') as tim_bertanding, s.nama 
            from tim_pertandingan as tp 
            inner join pertandingan as p on tp.id_pertandingan=p.id_pertandingan -- add a dot here
            inner join stadium as s on p.stadium=s.id_stadium -- change stadium to s
		    where (p.id_pertandingan) in 
            (select id_pertandingan 
            from tim_manajer natural 
            join tim_pertandingan where id_manajer='{id_manajer}')
            group by s.id_stadium, p.id_pertandingan
            order by start_datetime
            """
    cur.execute(query)
    list_pertandingan = cur.fetchall()
    context = {'pertandingans' : list_pertandingan}

    return render(request, 'list_pertandingan_manajer.html', context)

def history_rapat(request):
    id_manajer = request.COOKIES.get('id_role')

    query = f"""
    select array_to_string(array_agg("nama_tim"),' VS ') as rapat_tim, panitia.username as nama_panitia, stadium.nama as nama_stadium, pertandingan.start_datetime as tanggal_dan_waktu, rapat.id_pertandingan
    from rapat, panitia, tim_pertandingan, stadium, pertandingan
    where tim_pertandingan.id_pertandingan = rapat.id_pertandingan and pertandingan.id_pertandingan = rapat.id_pertandingan and pertandingan.stadium = stadium.id_stadium and rapat.perwakilan_panitia = panitia.id_panitia
    AND (manajer_tim_a='{id_manajer}' or manajer_tim_b='{id_manajer}')
    group by pertandingan.start_datetime, stadium.nama, panitia.username, rapat.id_pertandingan
    order by pertandingan.start_datetime
    """
    cur.execute(query)
    rapats = cur.fetchall()

    context = {
        'rapats':rapats
    }
    return render(request, 'history_rapat.html', context)

def isi_rapat(request):
    if (request.method == "POST"):

        data = json.loads(request.body)
        id_pertandingan = data.get('id_pertandingan')
        print(id_pertandingan + " ini id")

        response = HttpResponseRedirect(reverse('krem:isi_rapat'))
        response['location'] = reverse('krem:isi_rapat')

        response.set_cookie("id_pertandingan", id_pertandingan)

        print(response)
        return response


        query=f"""
        select isi_rapat from rapat where id_pertandingan = \'{id_pertandingan}\'
        """
        cur.execute(query)
        isi_rapat = cur.fetchall()

        response.set_cookie("id_pertandingan", id_pertandingan)


        context = {
            'isi_rapat': isi_rapat
        }

        return render(request, 'isi_rapat.html', context)
    if (request.method=="GET"):
        id_manajer = request.COOKIES.get('id_pertandingan')
        query=f"""
        select isi_rapat from rapat where id_pertandingan = '{id_manajer}'
        """
        cur.execute(query)
        isi_rapat = cur.fetchall()

        context = {
            'isi_rapat': isi_rapat
        }

        return render(request, 'isi_rapat.html', context)
        


def generate_random_receipt():
    random_numbers = [random.randint(1000, 9999) for _ in range(4)]
    random_string = '-'.join(map(str, random_numbers))
    return random_string


#test
def ex_query(request):
    cur.execute('select * from test')
    res = cur.fetchall()
    return HttpResponse(res)