import json
from django.shortcuts import render
import psycopg2
import psycopg2.extras
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed, JsonResponse, QueryDict
from django.urls import reverse
from putih.decorators.logged_in_decorators import login_required_as_role, login_required
from putih.views import json_format


# Create your views here.
conn = psycopg2.connect(database=settings.DATABASE_NAME, 
                        user=settings.DATABASE_USER, 
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST, 
                        port=settings.DATABASE_PORT, 
                        )

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

@login_required
@login_required_as_role('manajer')
def home(request):
    tim = get_tim_from_manajer(request.COOKIES.get('id_role'))
    if(tim != []):
        result = {"data":[]}
        for i in tim:
            result["data"].append({
                "tim": i,
                "pelatih": get_pelatih_from_tim(i.get("nama_tim")),
                "pemain": get_pemain_from_tim(i.get("nama_tim")),
            })
        return render(request, "tim.html", context=result)
    
    return render(request, 'mengelola_tim.html')

@login_required
@login_required_as_role('manajer')
def create_tim(request):
    if (request.method == "POST"):
        nama_tim = request.POST.get('nama-tim')
        nama_univ = request.POST.get('nama_univ')
        try:
            cur.execute('INSERT INTO TIM VALUES(%s, %s)', [nama_tim, nama_univ, ])
            conn.commit()
            return f'insert tim {nama_tim} with univ name {nama_univ} succeded'
        except Exception as e:
            conn.rollback()
            return HttpResponse(e)
    
    return HttpResponseNotAllowed("Invalid request method. Please use supported request method.")

@login_required
@login_required_as_role('manajer')
def add_pemain(request):
    cur.execute("SELECT * FROM PEMAIN WHERE nama_tim IS NULL")
    result = cur.fetchall()
    json_format(result)
    data = {
        "data":result
    }
    return render(request, "pemilihan_pemain.html", context=data)

@login_required
@login_required_as_role('manajer')
def add_pelatih(request):
    cur.execute("SELECT * FROM PELATIH WHERE nama_tim IS NULL")
    result = cur.fetchall()
    json_format(result)
    data = {
        "data":result
    }
    return render(request, "pemilihan_pelatih.html", context=data)


@login_required
@login_required_as_role('manajer')
def delete_pemain(request):
    if(request.method == "DELETE"):
        payload = QueryDict(request.body)
        id_pemain = payload.get('id_pemain')
        try:
            cur.execute("DELETE FROM PEMAIN WHERE id_pemain=%s",[id_pemain, ])
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)
            return HttpResponse("Unsuccessful")
        return HttpResponse("Success!")

    return HttpResponseNotAllowed("Invalid request method. Please use supported request method.")

@login_required
@login_required_as_role('manajer')
def update_captain(request):
    if(request.method == "PUT"):
        payload = QueryDict(request.body)
        id_pemain = payload.get('id_pemain')
        try:
            cur.execute("UPDATE PEMAIN SET is_captain=TRUE WHERE id_pemain=%s",[id_pemain, ])
            conn.commit()
        except Exception as e:
            conn.rollback()
            return HttpResponse("User is already a captain!")
        return HttpResponse("Success!")
    return HttpResponseNotAllowed("Invalid request method. Please use supported request method.")


def get_tim_from_manajer(id_manajer):
    cur.execute("SELECT * FROM TIM_MANAJER WHERE id_manajer = %s", [id_manajer, ])
    result = cur.fetchall()
    json_format(result)
    return result

def get_pemain_from_tim(nama_tim):
    cur.execute("SELECT * FROM PEMAIN WHERE nama_tim = %s", [nama_tim, ])
    result = cur.fetchall()
    json_format(result)
    return result

def get_pelatih_from_tim(nama_tim):
    cur.execute("SELECT * FROM PELATIH, NON_PEMAIN WHERE id = id_pelatih AND nama_tim = %s", [nama_tim, ])
    result = dict(cur.fetchone())
    cur.execute("SELECT spesialisasi FROM SPESIALISASI_PELATIH WHERE id_pelatih = %s", [result["id_pelatih"]])
    data = cur.fetchall()
    if (data != []):
        result['spesialisasi'] = [obj[0] for obj in cur.fetchall()]
    return result

