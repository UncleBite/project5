from django.db import models
from django.contrib.auth.models import User
# Create your models here.


class package(models.Model):
    worldid = models.CharField(max_length=30,null=True,default="")
    STATUS = (
        ('C', 'Created'),
        ('E', 'truck en route to warehouse'),
        ('W', 'truck waiting for package'),
        ('L', 'loaded and waiting for delivery'),
        ('O', 'out for delivery'),
        ('D', 'delivered'))
    status = models.CharField(max_length=30, choices=STATUS)
    product_name = models.CharField(max_length=1000)
    description = models.TextField()
    count = models.IntegerField()
    location_x = models.CharField(max_length=30,null=True)
    location_y = models.CharField(max_length=30,null=True)
    packageid = models.CharField(max_length=10,default="0")
    truckid = models.CharField(max_length=30,null=True,default="")
    name = models.CharField(max_length=1000, null=True,default="")
    class Meta:
        db_table = 'package'

class truck(models.Model):
    worldid = models.CharField(max_length=30,null=True,default="")
    truckid = models.CharField(max_length=30)
    packageid = models.CharField(max_length=10,default="0")
    location_x = models.CharField(max_length=30,null=True)
    location_y = models.CharField(max_length=30,null=True)
    STATUS = (
        ('I', 'idel'),
        ('E', 'truck en route to warehouse'),
        ('W', 'truck waiting for package'),
        ('L', 'loaded and waiting for delivery'),
        ('O', 'out for delivery'))
    status = models.CharField(max_length=30, choices=STATUS)
    class Meta:
        db_table = 'truck'