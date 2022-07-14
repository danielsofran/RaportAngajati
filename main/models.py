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

    def __str__(self):
        return self.nume

class Info(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    latitude = models.DecimalField(max_digits=11, decimal_places=8)
    lognitude = models.DecimalField(max_digits=11, decimal_places=8)
    datetime = models.DateTimeField(blank=True, default=datetime.datetime.strptime("01.01.2022 00:00:00", "%d.%m.%Y %H:%M:%S"))
    text = models.TextField(blank=True, max_length=300)

    def __str__(self):
        return f"{self.user.nume} {self.datetime.hour}:{self.datetime.minute}"

    @property
    def day(self): return self.datetime.day

    @property
    def date(self): return self.datetime.date()

    @property
    def time(self): return self.datetime.time()

class Intrare(Info): pass
class Iesire(Info): pass

class Comanda(Info):
    numar_comanda = models.CharField(blank=False, max_length=15, default="Cxxxx.xx")
    denumire = models.CharField(blank=False, max_length=20, default="")

    def __str__(self):
        return super().__str__() + " " + self.denumire

