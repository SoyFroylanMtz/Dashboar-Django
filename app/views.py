from django.shortcuts import render

#Crear vistas 
def index(request):
    return render(request,"index.html")

def reporte(request):
    return render(request,"reportes.html")