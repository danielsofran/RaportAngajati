import datetime, pytz
from . import geometry

# Create your models here.

from django.db import models
from django.contrib.auth.models import AbstractUser

from siteReport import settings

class Forma(models.Model):
    nume = models.CharField(blank=True, default="corp", max_length=15)
    tip = models.CharField(blank=False, default="Triunghi", choices=[("Cerc", "Cerc")], max_length=15)
    puncte = models.TextField(blank=False, default="0 0\n0 0")
    def getShape(self):
        model = None
        if self.tip == "Triunghi": model = geometry.Triunghi
        elif self.tip == "Patrulater": model = geometry.Patrulater
        elif self.tip == "Cerc": model = geometry.Cerc
        strpcts = self.puncte.split('\n')
        while "" in strpcts:
            strpcts.remove("")
        pcts = []
        for pctstr in strpcts:
            s = str(pctstr).replace('\r', '').split(' ')
            pcts.append([float(s[0]), float(s[1])])
        return model(*pcts)
    def __str__(self): return self.nume

    class Meta:
        verbose_name='Arie pe harta'
        verbose_name_plural='Arii pe harta'

class Harta(models.Model):
    nume = models.CharField(blank=True, default="Harta", max_length=15)
    adresa = models.CharField(blank=True, default="https://www.google.com/maps/dir/^^lat^^,^^long^^//@^^lat^^,^^long^^,21z", max_length=200)

    def getAdress(self, lat, long) -> str:
        if not isinstance(lat, str): lat = str(lat)
        if not isinstance(long, str): long = str(long)
        adr = self.adresa.replace('^^lat^^', lat)
        adr = adr.replace('^^long^^', long)
        return adr

    def __str__(self):
        return self.nume

    class Meta:
        verbose_name_plural='Harti'

class OwnSettings(models.Model):
    nrrecalcpoz = models.IntegerField(blank=False, default=3, verbose_name="Numarul de relocari")
    secafterrecalc = models.IntegerField(blank=False, default=60, verbose_name="Numarul de secunde dupa care este disponibila o relocare")
    disterror = models.FloatField(blank=False, default=10, verbose_name="Distanta in metrii acceptata ca eroare a calculului de locatie")
    program = models.CharField(blank=False, default="L Ma Mi J V S D", max_length=20)
    harta = models.ForeignKey(Harta, null=True, on_delete=models.DO_NOTHING)

    def __str__(self): return "Setare"

    class Meta:
        verbose_name='Setari proprii'
        verbose_name_plural='Setari'

class User(AbstractUser):
    nume = models.CharField(blank=False, max_length=50, default="Angajat")
    email = models.EmailField(blank=True, null=False)
    telefon = models.CharField(blank=True, null=False, default='0'*10, max_length=15)
    role = models.CharField(blank=False, default="Angajat", max_length=20)

    def __str__(self):
        return self.nume

    class Meta:
        verbose_name='Utilizator'
        verbose_name_plural='Utilizatori'

class Info(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)
    latitude = models.DecimalField(blank=True, max_digits=11, decimal_places=8)
    longitude = models.DecimalField(blank=True, max_digits=11, decimal_places=8)
    nrcalcloc = models.IntegerField(blank=True, default=1, verbose_name="Numarul de relocari")
    datetime = models.DateTimeField(blank=True, default=datetime.datetime.strptime("01.01.2022 00:00:00", "%d.%m.%Y %H:%M:%S"))
    text = models.TextField(blank=True, max_length=300, verbose_name="observatie")

    def getStrTime(self):
        now = self.datetime
        settings_time_zone = pytz.timezone(settings.TIME_ZONE)
        now = now.astimezone(settings_time_zone)
        return now.strftime("%H:%M")

    @property
    def getCoords(self):
        return f"{self.latitude},{self.longitude}"

    def __str__(self):
        return f"{self.user.nume} {self.getStrTime()}"

    @property
    def day(self): return self.datetime.day

    @property
    def date(self): return self.datetime.date()

    @property
    def time(self): return self.datetime.time()

class Intrare(Info):
    class Meta:
        verbose_name_plural='Intrari'
class Iesire(Info):
    class Meta:
        verbose_name_plural='Iesiri'

class Comanda(Info):
    numar_comanda = models.CharField(blank=False, max_length=15, default="Cxxxx.xx")
    denumire = models.CharField(blank=False, max_length=20, default="")

    def __str__(self):
        return super().__str__() + " " + self.numar_comanda + " " + self.denumire

    class Meta:
        verbose_name_plural='Comenzi'

