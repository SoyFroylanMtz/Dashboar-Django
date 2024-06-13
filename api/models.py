from django.db import models

class Producto(models.Model):
    codigo = models.CharField(max_length=200)

class Venta(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE)
