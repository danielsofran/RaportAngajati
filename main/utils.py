import datetime
import math

from django import utils
import pytz
from django.utils.timezone import activate, localtime
from django.contrib import messages

from . import models
from siteReport import settings

def getTime(info: models.Info = None):
    if info is None: now = utils.timezone.now()
    else: now = info.datetime
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

def getMinDistance(info: models.Info) -> float:
    def get_min_distance(position: list) -> float:
        # returneaza distanta in metrii pana la cea mai apropiata unitate
        forme = models.Forma.objects.all()
        minim = 2**32
        for forma in forme:
            pct = forma.getShape().closestPoint(position)
            dst = degToMeters(pct[0], pct[1], position[0], position[1])
            if dst < minim:
                minim = dst
        return minim
    return get_min_distance([info.latitude, info.longitude])

def locStr(info: models.Info) -> str:
    error = models.OwnSettings.objects.all()[0].disterror
    dst = getMinDistance(info)
    diff = dst - error
    if diff <= 0:
        return "In firma"
    elif diff <= 500:
        return f"La {int(diff)} merti de firma"
    return f"La {diff/1000:.2f} km de firma"

def secureStr(text) -> str:
    return str(text).replace("script", "")

def isEqual(user, request) -> bool:
    return user.username == request.POST['user'] and \
           user.email == request.POST['email'] and \
           user.telefon == request.POST['tel'] and \
           user.password == request.POST['pwd']

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

def validAccountModif(request) -> bool:
    tel = str(request.POST['tel'])
    tel.replace(' ', '')
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
    return True