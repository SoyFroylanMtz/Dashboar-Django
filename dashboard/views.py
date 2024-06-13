from django.shortcuts import render
from django.db import connection
import json
from django.http import JsonResponse
from decimal import Decimal



# Create your views here.
def index(request):
    return render(request, "dashboard.html")


def calcular_porcentaje_no_vendidos():
    with connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS total_productos FROM inventario_final")
        total_productos = cursor.fetchone()[0]

        cursor.execute("""
            SELECT COUNT(*) AS total_no_vendidos
            FROM inventario_final p
            LEFT JOIN ventas_finales v ON p.Codigo = v.ProdID
            WHERE v.ProdID IS NULL
        """)
        total_no_vendidos = cursor.fetchone()[0]

        porcentaje_vendidos = (total_no_vendidos * 100) / total_productos if total_productos > 0 else 0
        porcentaje_no_vendidos = 100 - porcentaje_vendidos

    return round(porcentaje_no_vendidos)

def get_margen_promedio():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                Proveedor,
                SUM(SQRT(POW(Precio - PrecioC, 2))) / COUNT(CASE WHEN PrecioC > 0 THEN 1 END) AS Margen_Promedio
            FROM 
                inventario_final
            WHERE 
                PrecioC > 0
            GROUP BY 
                Proveedor;
        """)
        rows = cursor.fetchall()
    return rows

def calcular_fri():
    with connection.cursor() as cursor:
        # Calcular el Costo de los Bienes Vendidos
        cursor.execute("""
            SELECT SUM(v.Cantidad * p.PrecioC) AS Costo_Bienes_Vendidos
            FROM ventas_finales v
            JOIN inventario_final p ON v.ProdID = p.Codigo
            WHERE p.PrecioC > 0;
        """)
        costo_bienes_vendidos = cursor.fetchone()[0] or 0

        # Calcular el Promedio de Inventario
        cursor.execute("""
            SELECT AVG(p.PrecioC * p.Existentes) AS Promedio_Inventario
            FROM inventario_final p;
        """)
        promedio_inventario = cursor.fetchone()[0] or 0

        # Calcular FRI
        if promedio_inventario > 0:
            fri = costo_bienes_vendidos / promedio_inventario
        else:
            fri = 0

    return round(fri, 2)

def obtener_ventas_por_mes():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT
    DATE_FORMAT(STR_TO_DATE(v.Fecha, '%d/%m/%Y'), '%Y-%m') AS Mes,
    SUM(v.Cantidad * v.Precio) AS Total_Ventas
FROM
    ventas_finales v
WHERE
    STR_TO_DATE(v.Fecha, '%d/%m/%Y') BETWEEN '2023-01-01' AND '2024-05-31'
GROUP BY
    Mes
ORDER BY
    Mes;

        """)
        ventas_por_mes = cursor.fetchall()
    return ventas_por_mes



def obtener_proveedores_top_vendedores():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.Proveedor,
                SUM(v.Cantidad) AS Total_Vendido
            FROM 
                ventas_finales v
            JOIN 
                inventario_final p ON v.ProdID = p.Codigo
            GROUP BY 
                p.Proveedor
            ORDER BY 
                Total_Vendido DESC
            LIMIT 3;
        """)
        proveedores_top_vendedores = cursor.fetchall()
    return proveedores_top_vendedores


def dashboard(request):
    porcentaje_no_vendidos = calcular_porcentaje_no_vendidos()
    margen_promedio_data = get_margen_promedio()
    proveedores = [row[0] for row in margen_promedio_data]
    margenes = [float(row[1]) for row in margen_promedio_data]
    fri = calcular_fri()
    proveedores_top_vendedores = obtener_proveedores_top_vendedores()
    proveedores_top_vendedores = [
        (row[0], float(row[1])) for row in proveedores_top_vendedores
    ]

    ventas_por_mes = obtener_ventas_por_mes()
    meses = [row[0] for row in ventas_por_mes]
    total_ventas = [float(row[1]) for row in ventas_por_mes]

    context = {
        'porcentaje_no_vendidos': porcentaje_no_vendidos,
        'proveedores': json.dumps(proveedores),
        'margenes': json.dumps(margenes),
        'fri': fri,
        'proveedores_top_vendedores': json.dumps(proveedores_top_vendedores),
        'meses': json.dumps(meses),
        'total_ventas': json.dumps(total_ventas)
    }
    return render(request, 'dashboard.html', context)
def obtener_ventas_por_mes():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                DATE_FORMAT(STR_TO_DATE(v.Fecha, '%d/%m/%Y'), '%b') AS Mes,
                SUM(v.Cantidad * v.Precio) AS Total_Ventas
            FROM 
                ventas_finales v
            WHERE 
                STR_TO_DATE(v.Fecha, '%d/%m/%Y') BETWEEN '2024-01-01' AND '2024-05-31'
            GROUP BY 
                DATE_FORMAT(STR_TO_DATE(v.Fecha, '%d/%m/%Y'), '%b'),
                YEAR(STR_TO_DATE(v.Fecha, '%d/%m/%Y')),
                MONTH(STR_TO_DATE(v.Fecha, '%d/%m/%Y'))
            ORDER BY 
                YEAR(STR_TO_DATE(v.Fecha, '%d/%m/%Y')),
                MONTH(STR_TO_DATE(v.Fecha, '%d/%m/%Y'));

        """)
        ventas_por_mes = cursor.fetchall()
    return ventas_por_mes

def obtener_productos_mas_vendidos():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.Nombre, 
                SUM(v.Cantidad) AS Total_Vendido
            FROM 
                ventas_finales v
            JOIN 
                inventario_final p ON v.ProdID = p.Codigo
            GROUP BY 
                p.Nombre
            ORDER BY 
                Total_Vendido DESC
            LIMIT 20;
        """)
        productos_mas_vendidos = cursor.fetchall()
    return productos_mas_vendidos

def obtener_productos_menos_vendidos():
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT 
                p.Nombre, 
                SUM(v.Cantidad) AS Total_Vendido
            FROM 
                ventas_finales v
            JOIN 
                inventario_final p ON v.ProdID = p.Codigo
            GROUP BY 
                p.Nombre
            ORDER BY 
                Total_Vendido ASC
            LIMIT 10;
        """)
        productos_menos_vendidos = cursor.fetchall()
    return productos_menos_vendidos

def reporte(request):
    tipo_reporte = request.GET.get('tipo', 'mas_vendidos')

    if tipo_reporte == 'menos_vendidos':
        productos = obtener_productos_menos_vendidos()
    else:
        productos = obtener_productos_mas_vendidos()

    productos_serializables = [
        {'nombre': producto[0], 'total': float(producto[1])}
        for producto in productos
    ]

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse(productos_serializables, safe=False)

    # Si no es una solicitud AJAX, renderiza la página normalmente (opcional)
    context = {
        'productos_mas_vendidos': productos,
    }
    return render(request, 'reporte.html', context)