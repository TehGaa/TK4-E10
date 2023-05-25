from django.shortcuts import render
import psycopg2
import psycopg2.extras
import json
from django.http import HttpResponse, HttpResponseNotAllowed, HttpResponseBadRequest, HttpResponseRedirect, JsonResponse, QueryDict
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
import uuid

from putih.decorators.logged_in_decorators import login_required, login_required_as_role

# Create your views here.
conn = psycopg2.connect(database=settings.DATABASE_NAME,
                        user=settings.DATABASE_USER,
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST,
                        port=settings.DATABASE_PORT,
                        )

cur = conn.cursor()

def index(request):
    return render(request, 'index.html')

@login_required
@login_required_as_role('manajer')
def pinjam_stadium(request):
    query = f"SELECT nama, start_datetime, end_datetime FROM peminjaman, stadium WHERE peminjaman.id_stadium = stadium.id_stadium;"
    cur.execute(query)
    res = cur.fetchall()
    context = {'peminjaman_list': res}
    return render(request, 'peminjaman-stadium.html', context)

@login_required
@login_required_as_role('manajer')
def pinjam_stadium_form(request):
    query = "SELECT * FROM stadium"
    cur.execute(query)
    res = cur.fetchall()
    context = {'stadium_list' : res}
    return render(request, 'peminjaman-stadium-form.html', context)

@login_required
@login_required_as_role('manajer')
def tambah_peminjaman_stadium(request):
    id_manajer = request.COOKIES.get("id_role")
    stadium = request.POST['stadium']
    start_datetime = request.POST['start_date']
    end_datetime = request.POST['end_date']
    print(request.POST)
    try:
        cur.execute(
            "INSERT INTO peminjaman (id_manajer, start_datetime, end_datetime, id_stadium) VALUES (%s, %s, %s, %s);",
            [id_manajer, start_datetime, end_datetime, stadium])
        conn.commit()
        return HttpResponse("Berhasil")
    except Exception as e:
        conn.rollback()
        return HttpResponseBadRequest(e)
    return render(request, 'index.html')

@login_required
@login_required_as_role('panitia')
def mulai_rapat(request):
    query = """
            SELECT DISTINCT ON (B.id_pertandingan) B.id_pertandingan, A.nama_tim AS nama_tim_a, B.nama_tim AS nama_tim_b, P.start_datetime, P.end_datetime, S.nama AS nama_stadium
            FROM tim_pertandingan AS A
            JOIN tim_pertandingan AS B ON A.id_pertandingan = B.id_pertandingan AND A.nama_tim != B.nama_tim
            JOIN pertandingan AS P ON A.id_pertandingan = P.id_pertandingan
            JOIN stadium AS S ON P.stadium = S.id_stadium
            WHERE NOT EXISTS (
                SELECT 1
                FROM rapat
                WHERE rapat.id_pertandingan = A.id_pertandingan
            );
                """
    cur.execute(query)
    data = cur.fetchall()
    context = {'pertandingan_list': data}
    return render(request, 'mulai-rapat.html', context)

@login_required
@login_required_as_role('panitia')
def isi_rapat(request, pertandingan_id):
    query = """
        SELECT DISTINCT ON (B.id_pertandingan) B.id_pertandingan, A.nama_tim AS nama_tim_a, B.nama_tim AS nama_tim_b
        FROM tim_pertandingan AS A, tim_pertandingan AS B
        WHERE A.id_pertandingan = B.id_pertandingan AND A.nama_tim != B.nama_tim AND A.id_pertandingan = %s;
    """

    cur.execute(query, [str(pertandingan_id)])
    data = cur.fetchone()
    return render(request, 'isi-rapat.html', {'pertandingan': data})

@login_required
@login_required_as_role('panitia')
def process_isi_rapat(request):
    id_pertandingan = request.POST.get('pertandinganId')
    hasil_rapat = request.POST.get('isiRapat', '')
    perwakilan_panitia = request.COOKIES.get("id_role")
    cur.execute("""
            SELECT DISTINCT ON (B.id_pertandingan)
    B.id_pertandingan,
    A.nama_tim AS nama_tim_a,
    B.nama_tim AS nama_tim_b,
    MA.id_manajer AS id_manajer_a,
    MB.id_manajer AS id_manajer_b,
    P.start_datetime
FROM
    tim_pertandingan AS A
    JOIN tim_pertandingan AS B ON A.id_pertandingan = B.id_pertandingan AND A.nama_tim != B.nama_tim
    JOIN tim_manajer AS MA ON A.nama_tim = MA.nama_tim
    JOIN tim_manajer AS MB ON B.nama_tim = MB.nama_tim
    JOIN pertandingan AS P ON A.id_pertandingan = P.id_pertandingan
WHERE A.id_pertandingan=%s;
        """, [str(id_pertandingan)])
    fetch = cur.fetchone()
    data = {'data': fetch}
    print(data)
    manajer_tim_a = data.get('data')[3]
    manajer_tim_b = data.get('data')[4]
    datetime = data.get('data')[5]
    query ="""
    INSERT INTO rapat (id_pertandingan, datetime, perwakilan_panitia, manajer_tim_a, manajer_tim_b, isi_rapat)
VALUES (%s, %s, %s, %s, %s, %s);
    """

    try:
        cur.execute(query, [id_pertandingan, datetime, perwakilan_panitia, manajer_tim_a, manajer_tim_b, hasil_rapat])
        conn.commit()
        return HttpResponseRedirect(reverse('pink:mulai_rapat'))
    except Exception as e:
        conn.rollback()
        return HttpResponseBadRequest(e)
    return HttpResponseRedirect(reverse('pink:mulai_rapat'))