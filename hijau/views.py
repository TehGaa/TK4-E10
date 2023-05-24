from django.shortcuts import render
import psycopg2
import psycopg2.extras
from django.conf import settings
from django.http import HttpResponseBadRequest, HttpResponse, HttpResponseRedirect, HttpResponseNotAllowed
from django.urls import reverse
from putih.decorators.logged_in_decorators import login_required_as_role

# Create your views here.
conn = psycopg2.connect(database=settings.DATABASE_NAME, 
                        user=settings.DATABASE_USER, 
                        password=settings.DATABASE_PASSWORD,
                        host=settings.DATABASE_HOST, 
                        port=settings.DATABASE_PORT, 
                        )

cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

@login_required_as_role('manajer')
def home(request):
    if (request.method == 'POST'):
        nama_tim = request.POST.get('nama-tim')
        nama_univ = request.POST.get('nama-univ')
        
        cur.execute("SELECT * FROM TIM WHERE nama_tim = %s AND nama_univ = %s", [nama_tim, nama_univ, ])
        is_registered = cur.fetchall() == []
        
        if (is_registered):
            return f"Not Registered"
        
        response = HttpResponseRedirect(reverse('hijau:show_tim'))
        
        return 
    return render(request, 'mengelola_tim.html')

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

@login_required_as_role('manajer')
def show_tim(request):
    pass
