from django.shortcuts import render
from .models import Producto, Venta

def dashboard(request):
    total_productos = Producto.objects.count()
    productos_vendidos = Venta.objects.values('producto').distinct().count()

    # Calcula el porcentaje de productos no vendidos
    porcentaje_no_vendidos = ((total_productos - productos_vendidos) / total_productos) * 100

    return render(request, 'dashboard.html', {'porcentaje_no_vendidos': porcentaje_no_vendidos})
