import datetime
import math

import haversine as hs
import pytz
from django import utils
from django.contrib import messages
from django.utils.timezone import activate
from haversine import Unit

from siteReport import settings
from . import models


def getTime(info = None):
    now = None
    if info is None: now = utils.timezone.now()
    elif isinstance(info, models.Info): now = info.datetime
    elif isinstance(info, datetime.datetime): now = info
    settings_time_zone = pytz.timezone(settings.TIME_ZONE)
    now = now.astimezone(settings_time_zone)
    return now

def getNextDay(curent: datetime.datetime) -> datetime.datetime:
    program = models.OwnSettings.objects.all()[0].program
    asocs = {
        "L": "Monday",
        "Ma": "Tuesday",
        "Mi": "Wednesday",
        "J": "Thursday",
        "V": "Friday",
        "S": "Saturday",
        "D": "Sunday",
    }
    engpr = []
    for day in program.split(' '):
        for abrev in asocs:
            if day.startswith(abrev):
                engpr.append(asocs[abrev])
    curent = curent + datetime.timedelta(days=1)
    while curent.strftime("%A") not in engpr:
        curent = curent + datetime.timedelta(days=1)
    return curent

def getPrevDay(curent: datetime.datetime) -> datetime.datetime:
    program = models.OwnSettings.objects.all()[0].program
    asocs = {
        "L": "Monday",
        "Ma": "Tuesday",
        "Mi": "Wednesday",
        "J": "Thursday",
        "V": "Friday",
        "S": "Saturday",
        "D": "Sunday",
    }
    engpr = []
    for day in program.split(' '):
        for abrev in asocs:
            if day.startswith(abrev):
                engpr.append(asocs[abrev])
    curent = curent - datetime.timedelta(days=1)
    while curent.strftime("%A") not in engpr:
        curent = curent - datetime.timedelta(days=1)
    return curent

def rangeDays(datatimein: datetime.datetime, datetimeout: datetime.datetime):
    rez = []
    while datatimein <= datetimeout:
        #print(datatimein)
        rez.append(datatimein)
        datatimein = getNextDay(datatimein)
    return rez

def getMinDistance(info: models.Info):
    def get_min_distance(position: tuple):
        # returneaza distanta in metrii pana la cea mai apropiata unitate
        forme = models.Forma.objects.all()
        minim = 2**32
        formamin = None
        for forma in forme:
            shape = forma.getShape()
            dc = hs.haversine(shape.center, position, unit=Unit.METERS)
            raza = hs.haversine(shape.center, shape.point, unit=Unit.METERS)
            diff = dc - raza
            if diff < 0: diff = 0
            minim = min(minim, diff)
            formamin = forma
        return minim, formamin.nume
    return get_min_distance((info.latitude, info.longitude))

def locStr(info: models.Info) -> str:
    error = models.OwnSettings.objects.all()[0].disterror
    try: dst = getMinDistance(info)
    except: return "-"
    diff = dst[0] - error
    if diff <= 0:
        return "In firma"
    elif diff <= 500:
        return f"La {int(diff)} merti de firma"
    return f"La {diff/1000:.2f} km de firma"

def secureStr(text) -> str:
    return str(text).replace("script", "")

def isEqual(user, request) -> bool:
    c1=    user.username == request.POST['user'] and \
           user.email == request.POST['email'] and \
           user.telefon == request.POST['tel'] and \
           user.password == request.POST['pwd']
    c2 = True
    if request.user.role == "Manager" or request.user.role == "Admin":
        c2 = user.nume == request.POST['nume'] and \
             user.role == request.POST['role']
    return c1 and c2

def degToMeters(lat1, lon1, lat2, lon2) -> float:
    R = 6387.137 # Radius of earth in km
    dLat = lat2 * math.pi / 180 - lat1 * math.pi / 180
    dLon = lon2 * math.pi / 180 - lon1 * math.pi / 180
    a = math.sin(dLat/2) * math.sin(dLat/2) + \
        math.cos(lat1 * math.pi / 180) * math.cos(lat2 * math.pi / 180) * \
        math.sin(dLon/2) * math.sin(dLon/2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    d = R * c
    return d * 1000

def validLoc(loc: str):
    if loc.count(',') != 1: return False
    if loc.count('.') != 2: return False
    for cif in loc:
        if cif in ' ,.': continue
        if cif >= '0' and cif <= '9': continue
        return False
    return True

def validTel(tel: str):
    tel.replace(' ', '')
    if tel.__len__() < 10:
        #messages.success(request, ("Numarul de telefon nu contine destule cifre!"))
        return False
    if (tel[0] < '0' or tel[0] > '9') and tel[0] != '+':
        #messages.success(request, ("Prima cifra a numarului de telefon este invalida!"))
        return False
    for cif in tel[1:]:
        if cif not in '.-' and (cif < '0' or cif > '9'):
            #messages.success(request, ("Numar de telefon invalid!"))
            return False
    return True

def validAccountModif(user, request) -> bool:
    if len(str(request.POST['user'])) < 5:
        messages.success(request, ("Numele de utilizator ar trebui sa aiba cel putin 5 caractere."))
        return False
    if user.username != request.POST['user']:
        try:
            anotherusername = models.User.objects.get(username=request.POST['user'])
            messages.success(request, ("Acest nume de utilizator exista deja!\nIncercati altul."))
            return False
        except: pass

    tel = str(request.POST['tel'])
    tel.replace(' ', '')
    if tel.__len__() != 0:
        if tel.__len__() < 10:
            messages.success(request, ("Numarul de telefon nu contine destule cifre!"))
            return False
        if (tel[0]<'0' or tel[0]>'9') and tel[0] != '+':
            messages.success(request, ("Prima cifra a numarului de telefon este invalida!"))
            return False
        for cif in tel[1:]:
            if cif not in '.-' and (cif<'0' or cif>'9'):
                messages.success(request, ("Numar de telefon invalid!"))
                return False
    parola = str(request.POST['pwd'])
    if len(parola) < 8:
        messages.success(request, ("Parola trebuie sa contina minim 8 caractere!"))
        return False

    if user.role == "Manager" or user.role == "Admin":
        if request.POST['role'] not in ('Angajat', 'Vizualizator', 'Manager', 'Admin'):
            messages.success(request, ("Statut invalid!"))
            return False
        if len(request.POST['nume']) < 3:
            messages.success(request, ("Nume prea scurt!"))
            return False
    return True

class MyException(Exception): pass

def fromCsv():
    from siteReport import settings
    import os
    with open(os.path.join(settings.BASE_DIR, 'csvFinal.csv')) as file:
        for line in file:
            line = line[:-1]
            tokens = line.split(',')
            _, created = models.User.objects.get_or_create(
                username=tokens[1],
                password=tokens[2],
                nume=tokens[0],
                role="Angajat",
            )