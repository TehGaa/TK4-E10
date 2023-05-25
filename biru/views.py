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
from putih.decorators.logged_in_decorators import *
import uuid


# Create your views here.
conn = psycopg2.connect(database=settings.DATABASE_NAME, 
                        user=settings.DATABASE_USER, 
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST, 
                        port=settings.DATABASE_PORT, 
                        )

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

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
                SELECT S.Nama, S.id_stadium
                FROM Stadium AS S;
            """

            cur.execute(query)
            data = fetch(cur)
            response = {'data': data}
            print(response)
            
            return render(request, 'dropdown_stadium.html', response)

def create_pertandingan(request):
    if (request.method == "POST"):
        nama_stadium = request.POST.get("stadium")
        tanggal = request.POST.get("tanggal")
        print('haha')
        print(nama_stadium)
        print(tanggal)
        request.session['nama_stadium'] = nama_stadium
        request.session['tanggal'] = tanggal

        query_wasit = """
        SELECT nama_depan||' '||nama_belakang as nama, w.id_wasit
        FROM wasit as w, non_pemain
        WHERE NON_PEMAIN.id = w.id_wasit;
        """
        query_tim = f"select nama_tim from tim_manajer natural join peminjaman inner join stadium on peminjaman.id_stadium=stadium.id_stadium where stadium.id_stadium='{nama_stadium}';"

        # query_tim = f"select nama_tim from tim;"
        cur.execute(query_wasit)
        data_w = fetch(cur)

        cur.execute(query_tim)
        data_t = fetch(cur)
        # print(data_t)

        response = {'data_w': data_w, 'data_t': data_t, 'nama stadium': nama_stadium}
        # print(response)
        # print(nama_stadium)
        return render(request, 'create_pertandingan.html', response)
            
# INI BIKIN CREATE REALLL

def submit_create_pertandingan(request):
    if (request.method == "POST"):
        wasitutama = request.POST.get("wasitutama")
        wasitpembantu1 = request.POST.get("wasitpembantu1")
        wasitpembantu2 = request.POST.get("wasitpembantu2")
        wasitcadangan = request.POST.get("wasitcadangan")
        tim1 = request.POST.get("tim1")
        tim2 = request.POST.get("tim2")

        print(request.session)
        stadium = request.session.get('nama_stadium')
        tanggal = request.session.get('tanggal')
        print(stadium)

        try:
            psycopg2.extras.register_uuid()

            uuid_for_id_pertandingan = generate_uuid()
            print(uuid_for_id_pertandingan)
            print(stadium)

            cur.execute("INSERT INTO PERTANDINGAN VALUES(%s, %s, %s, %s)",
                        [uuid_for_id_pertandingan, tanggal, tanggal, stadium])
            cur.execute("INSERT INTO TIM_PERTANDINGAN VALUES(%s, %s, %s)", [tim1, uuid_for_id_pertandingan, 0])
            cur.execute("INSERT INTO TIM_PERTANDINGAN VALUES(%s, %s, %s)", [tim2, uuid_for_id_pertandingan, 0])
            cur.execute("INSERT INTO WASIT_BERTUGAS VALUES(%s, %s, %s)", [wasitutama, uuid_for_id_pertandingan, 'utama'])
            cur.execute("INSERT INTO WASIT_BERTUGAS VALUES(%s, %s, %s)", [wasitpembantu1, uuid_for_id_pertandingan, 'pembantu'])
            cur.execute("INSERT INTO WASIT_BERTUGAS VALUES(%s, %s, %s)", [wasitpembantu2, uuid_for_id_pertandingan, 'pembantu'])
            cur.execute("INSERT INTO WASIT_BERTUGAS VALUES(%s, %s, %s)", [wasitcadangan, uuid_for_id_pertandingan, 'cadangan'])
            conn.commit()

            return redirect(reverse('biru:data_list_pertandingan'))
        except Exception as e:
            conn.rollback()
            return HttpResponse(e)
    
    return HttpResponseNotAllowed("Invalid request method. Please use supported request method.")

# INI GENERATE ID

def generate_uuid():
    while (True):
        generated_uuid = uuid.uuid4()
        cur.execute("SELECT * FROM PERTANDINGAN WHERE id_pertandingan = %s", (generated_uuid,))
        lst_pertandingan = cur.fetchall()
        if (lst_pertandingan == []):
            return generated_uuid

# II KSAK LITAAAAAAAAAA

def delete_pertandingan(request):
	delete_tim_pertandingan(request.POST)
	return redirect("biru:data_list_pertandingan")

def delete_tim_pertandingan(data):
    query = f"""
    DELETE FROM rapat
    WHERE id_pertandingan = '{data['id_pertandingan']}';
    DELETE FROM tim_pertandingan
    WHERE id_pertandingan = '{data['id_pertandingan']}';
    DELETE FROM pembelian_tiket
    WHERE id_pertandingan = '{data['id_pertandingan']}';
    DELETE FROM wasit_bertugas
    WHERE id_pertandingan = '{data['id_pertandingan']}';
    DELETE FROM peristiwa
    WHERE id_pertandingan = '{data['id_pertandingan']}';
    DELETE FROM wasit_bertugas
    WHERE id_pertandingan = '{data['id_pertandingan']}';
    DELETE FROM pembelian_tiket
    WHERE id_pertandingan = '{data['id_pertandingan']}';
    DELETE FROM pertandingan
    WHERE id_pertandingan = '{data['id_pertandingan']}';
    """
    cur.execute(query)
    conn.commit()

# INI MAU COBA UPDATEEEEEEEEE

def update_dropdown_stadium(request):
    if (request.method == "POST"):
        id_pertandingan = request.POST.get("id_pertandingan")
        request.session['id_pertandingan'] = id_pertandingan
                
        query_selected = f"""
            SELECT S.Nama, S.id_stadium, T.id_pertandingan, p.Start_Datetime, p.End_Datetime
            FROM Stadium AS S, tim_pertandingan as t, pertandingan as p
            WHERE S.id_stadium=p.stadium AND p.id_pertandingan='{id_pertandingan}';
        """
        query_all = f"""
                SELECT S.Nama, S.id_stadium
                FROM Stadium AS S;
            """
        cur.execute(query_selected)
        data_selected = fetch(cur)
        
        cur.execute(query_all)
        data_all = fetch(cur)
        response = {'data_all': data_all, 'data_selected': data_selected,}
        return render(request, 'update_dropdown_stadium.html', response)
    
def update_create_pertandingan(request):
    if (request.method == "POST"):
        nama_stadium = request.POST.get("stadium")
        tanggal = request.POST.get("tanggal")
        print('haha')
        print(nama_stadium)
        print(tanggal)
        request.session['nama_stadium'] = nama_stadium
        request.session['tanggal'] = tanggal
        id_pertandingan = request.session.get('id_pertandingan')

        query_wasit = """
        SELECT nama_depan||' '||nama_belakang as nama, w.id_wasit
        FROM wasit as w, non_pemain
        WHERE NON_PEMAIN.id = w.id_wasit;
        """
        query_tim = f"select nama_tim from tim_manajer natural join peminjaman inner join stadium on peminjaman.id_stadium=stadium.id_stadium where stadium.id_stadium='{nama_stadium}';"

        # qwasitutama = f"""
        # SELECT DISTINCT n.nama_depan||' '||n.nama_belakang as nama, w.id_wasit
        # FROM wasit as w, non_pemain as n, pertandingan as p, wasit_bertugas as t
        # WHERE (n.id = w.id_wasit AND T.id_wasit=w.id_wasit 
        # AND n.id = T.id_wasit AND p.id_pertandingan=T.id_pertandingan 
        # AND p.id_pertandingan='{id_pertandingan}' 
        # AND t.posisi_wasit='utama');
        # """
        # qwasitpembantu= f"""
        # SELECT DISTINCT n.nama_depan||' '||n.nama_belakang as nama, w.id_wasit
        # FROM wasit as w, non_pemain as n, pertandingan as p, wasit_bertugas as t
        # WHERE (n.id = w.id_wasit AND T.id_wasit=w.id_wasit 
        # AND n.id = T.id_wasit AND p.id_pertandingan=T.id_pertandingan 
        # AND p.id_pertandingan='{id_pertandingan}' 
        # AND t.posisi_wasit='pembantu');
        # """
        # qwasitcadangan = f"""
        # SELECT DISTINCT n.nama_depan||' '||n.nama_belakang as nama, w.id_wasit
        # FROM wasit as w, non_pemain as n, pertandingan as p, wasit_bertugas as t
        # WHERE (n.id = w.id_wasit AND T.id_wasit=w.id_wasit 
        # AND n.id = T.id_wasit AND p.id_pertandingan=T.id_pertandingan 
        # AND p.id_pertandingan='{id_pertandingan}' 
        # AND t.posisi_wasit='cadangan');
        # """
        # qtim = f"select nama_tim from tim_manajer natural join peminjaman inner join stadium on peminjaman.id_stadium=stadium.id_stadium where stadium.id_stadium='{nama_stadium}';"

        # query_tim = f"select nama_tim from tim;"
        cur.execute(query_wasit)
        data_w = fetch(cur)

        cur.execute(query_tim)
        data_t = fetch(cur)
        # print(data_t)

        response = {'data_w': data_w, 'data_t': data_t, 'nama stadium': nama_stadium}
        # print(response)
        # print(nama_stadium)
        return render(request, 'update_create_pertandingan.html', response)

def update_submit_create_pertandingan(request):
    if (request.method == "POST"):
        wasitutama = request.POST.get("wasitutama")
        wasitpembantu1 = request.POST.get("wasitpembantu1")
        wasitpembantu2 = request.POST.get("wasitpembantu2")
        wasitcadangan = request.POST.get("wasitcadangan")
        tim1 = request.POST.get("tim1")
        tim2 = request.POST.get("tim2")

        print(request.session)
        stadium = request.session.get('nama_stadium')
        tanggal = request.session.get('tanggal')
        print(stadium)
        id_pertandingan = request.session.get('id_pertandingan')

        try:
            cur.execute("UPDATE WASIT_BERTUGAS SET id_wasit = %s WHERE id_pertandingan = %s AND Posisi_Wasit = %s",
                        [wasitutama, id_pertandingan, 'utama'])
            cur.execute("UPDATE WASIT_BERTUGAS SET id_wasit = %s WHERE id_pertandingan = %s AND Posisi_Wasit = %s",
                        [wasitpembantu1, id_pertandingan, 'pembantu'])
            cur.execute("UPDATE WASIT_BERTUGAS SET id_wasit = %s WHERE id_pertandingan = %s AND Posisi_Wasit = %s",
                        [wasitpembantu2, id_pertandingan, 'pembantu'])
            cur.execute("UPDATE WASIT_BERTUGAS SET id_wasit = %s WHERE id_pertandingan = %s AND Posisi_Wasit = %s",
                        [wasitcadangan, id_pertandingan, 'cadangan'])
            cur.execute("UPDATE PERTANDINGAN SET Start_Datetime = %s, End_Datetime = %s, stadium = %s WHERE id_pertandingan = %s",
            [tanggal, tanggal, stadium, id_pertandingan])
            cur.execute("UPDATE TIM_PERTANDINGAN SET Nama_Tim = %s WHERE id_pertandingan = %s",
                        [tim2, id_pertandingan])
            cur.execute("UPDATE TIM_PERTANDINGAN SET Nama_Tim = %s WHERE id_pertandingan = %s",
                        [tim1, id_pertandingan])
            conn.commit()

            return redirect(reverse('biru:data_list_pertandingan'))
        except Exception as e:
            conn.rollback()
            return HttpResponse(e)
    
    return HttpResponseNotAllowed("Invalid request method. Please use supported request method.")
