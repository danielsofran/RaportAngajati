import datetime

from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    nume = models.CharField(blank=False, max_length=50, default="Angajat")
    email = models.EmailField(blank=True, null=False)
    telefon = models.CharField(blank=True, null=False, default='0'*10, max_length=15)
    role = models.CharField(blank=False, default="Angajat", max_length=20)

class Info(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    lognitude = models.DecimalField(max_digits=9, decimal_places=6)
    time = models.DateTimeField(blank=True, default=datetime.datetime.strptime("01.01.2022 00:00:00", "%d.%m.%Y %H:%M:%S"))
    observatie = models.TextField(blank=True, max_length=300)