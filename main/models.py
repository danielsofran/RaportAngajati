import datetime
import pytz

from django.db import models

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser

from siteReport import settings


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
    longitude = models.DecimalField(max_digits=11, decimal_places=8)
    nrcalcloc = models.IntegerField(blank=True, default=0)
    datetime = models.DateTimeField(blank=True, default=datetime.datetime.strptime("01.01.2022 00:00:00", "%d.%m.%Y %H:%M:%S"))
    text = models.TextField(blank=True, max_length=300)

    def getStrTime(self):
        now = self.datetime
        settings_time_zone = pytz.timezone(settings.TIME_ZONE)
        now = now.astimezone(settings_time_zone)
        return now.strftime("%H:%M")

    def __str__(self):
        return f"{self.user.username}-> {self.user.nume} {self.getStrTime()}"

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

