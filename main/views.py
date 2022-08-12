import itertools

import pytz
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.decorators import user_passes_test, login_required
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView

from siteReport import settings
from .utils import MyException
from .viewmodels import *


# Create your views here.

# region Login
def login_user(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']

        user = None

        try:
            user = models.User.objects.get(username=username, password=password)
        except:
            pass

        if user is not None:
            login(request, user)
            return redirect('home')

        try:
            user = models.User.objects.get(nume=username, password=password)
        except:
            pass

        if user is not None:
            login(request, user)
            return redirect('home')

        try:
            user = models.User.objects.get(email=username, password=password)
        except:
            pass

        if user is not None:
            login(request, user)
            return redirect('home')

        try:
            user = models.User.objects.get(telefon=username, password=password)
        except:
            pass

        if user is not None:
            login(request, user)
            return redirect('home')

        messages.success(request, ("Date de autentificare invalide!"))
        return HttpResponseRedirect(request.path_info)

    elif request.user.is_authenticated:
        return redirect('home')

    else:
        messages.success(request, ("Atentie! Acest site este dedicat strict angajatilor."))
        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    return redirect('mylogin')


# endregion

# region Home

# region Come Left

def come(request):
    if request.method == 'GET':
        now = utils.getTime()
        SEC_RECALC_AFTER = 60
        NR_RECALC_POZ = 3
        DIST_ERROR = 10
        try:
            setare = models.OwnSettings.objects.first()
            SEC_RECALC_AFTER = setare.secafterrecalc
            NR_RECALC_POZ = setare.nrrecalcpoz
            DIST_ERROR = setare.disterror
        except:
            print('Nu exista setari!')
        intrari = models.Intrare.objects.filter(user=request.user, datetime__day=now.day)
        iesiri = models.Iesire.objects.filter(user=request.user, datetime__day=now.day)
        if intrari.count() - iesiri.count() in (-1, 0):
            models.Intrare.objects.create(user=request.user, latitude=request.GET['lat'], longitude=request.GET['long'],
                                          datetime=now, nrcalcloc=1, text=utils.secureStr(request.GET['obs']))
            messages.success(request, ("Succes!"))
        else:
            messages.success(request, ("Nu puteti inregistra ajungerea!"))
            return redirect('home')
    else:
        print("POST in come")
    return redirect('home')

def cancel_come(request):
    now = utils.getTime()
    intrari = models.Intrare.objects.filter(user=request.user, datetime__day=now.day)
    iesiri = models.Iesire.objects.filter(user=request.user, datetime__day=now.day)
    if intrari.count() - iesiri.count() not in (1, 0) or intrari.count() == 0:
        messages.success(request, ("Nu puteti anula ajungerea!"))
        return redirect('home')
    data = intrari.order_by("-datetime").first()
    if data is None:
        messages.success(request, ("Momentul ajungerii nu a fost inregistrat!"))
        return redirect('home')
    data.delete()
    messages.success(request, ("Momentul ajungerii a fost sters!"))
    return redirect('home')

def recalc_come(request):
    SEC_RECALC_AFTER = 60
    NR_RECALC_POZ = 3
    try:
        setare = models.OwnSettings.objects.first()
        SEC_RECALC_AFTER = setare.secafterrecalc
        NR_RECALC_POZ = setare.nrrecalcpoz
    except:
        print("Nu exista setari")
    try:
        now = utils.getTime()
        data = models.Intrare.objects.filter(user=request.user, datetime__day=now.day).order_by("-datetime").first()
        if (now - utils.getTime(data)).seconds > SEC_RECALC_AFTER:
            raise ValueError("Timpul pentru relocare a expirat!")
        nr = data.nrcalcloc
        if nr <= NR_RECALC_POZ:
            data.nrcalcloc = data.nrcalcloc + 1
            data.latitude = request.GET['lat']
            data.longitude = request.GET['long']
            data.save(force_update=True, update_fields=['latitude', 'longitude', 'nrcalcloc'])
            messages.success(request,
                             (f"Locatie actualizata! Mai aveti {NR_RECALC_POZ + 1 - data.nrcalcloc} relocari."))
        else:
            messages.success(request, (f"Nu mai aveti relocari disponibile."))
    except:
        messages.success(request, ("Timpul pentru relocare a expirat!"))
    return redirect('actToday')

def left(request):
    now = utils.getTime()
    SEC_RECALC_AFTER = 60
    NR_RECALC_POZ = 3
    DIST_ERROR = 10
    try:
        setare = models.OwnSettings.objects.first()
        SEC_RECALC_AFTER = setare.secafterrecalc
        NR_RECALC_POZ = setare.nrrecalcpoz
        DIST_ERROR = setare.disterror
    except:
        print("Nu exista setari")
    intrari = models.Intrare.objects.filter(user=request.user, datetime__day=now.day)
    iesiri = models.Iesire.objects.filter(user=request.user, datetime__day=now.day)
    if intrari.count() - iesiri.count() not in (0, 1):
        messages.success(request, ("Nu puteti inregistra plecarea!"))
        return redirect('home')
    models.Iesire.objects.create(user=request.user, latitude=request.GET['lat'], longitude=request.GET['long'],
                                     datetime=now, nrcalcloc=1, text=utils.secureStr(request.GET['obs']))
    messages.success(request, ("Succes!"))
    return redirect('home')

def cancel_left(request):
    now = utils.getTime()
    intrari = models.Intrare.objects.filter(user=request.user, datetime__day=now.day)
    iesiri = models.Iesire.objects.filter(user=request.user, datetime__day=now.day)
    if intrari.count() - iesiri.count() not in (0, -1) or iesiri.count() == 0:
        messages.success(request, ("Momentul plecarii nu a fost inregistrat!"))
        return redirect('home')
    data = iesiri.order_by("-datetime").first()
    data.delete()
    messages.success(request, ("Momentul plecarii a fost sters!"))
    return redirect('home')

def recalc_left(request):
    now = utils.getTime()
    SEC_RECALC_AFTER = 60
    NR_RECALC_POZ = 3
    try:
        setare = models.OwnSettings.objects.first()
        SEC_RECALC_AFTER = setare.secafterrecalc
        NR_RECALC_POZ = setare.nrrecalcpoz
    except:
        print("Nu exista setari")
    try:
        data = models.Iesire.objects.filter(user=request.user, datetime__day=now.day).order_by("-datetime").first()
        if (now - utils.getTime(data)).seconds > SEC_RECALC_AFTER:
            raise ValueError("Timpul pentru relocare a expirat!")
        nr = data.nrcalcloc
        if nr <= NR_RECALC_POZ:
            data.nrcalcloc = data.nrcalcloc + 1
            data.latitude = request.GET['lat']
            data.longitude = request.GET['long']
            data.save(force_update=True, update_fields=['latitude', 'longitude', 'nrcalcloc'])
            messages.success(request,
                             (f"Locatie actualizata! Mai aveti {NR_RECALC_POZ + 1 - data.nrcalcloc} relocari."))
        else:
            messages.success(request, (f"Nu mai aveti relocari disponibile."))
    except:
        messages.success(request, ("Nu exista o locatie initiala ce poate fi actualizata"))
    return redirect('actToday')


# endregion

# region Comanda

def comandaFinish(request):
    if request.method == "GET":
        if 'nrcom' not in request.GET or len(request.GET['nrcom'])==0:
            messages.success(request, ("Numar comanda invalid!"))
            return redirect('home')
        if 'den' not in request.GET or len(request.GET['den'])==0:
            messages.success(request, ("Denumire invalida!"))
            return redirect('home')
        now = utils.getTime()
        # try:
        #     intraris =models.Intrare.objects.filter(user=request.user, datetime__day=now.day, datetime__lte=now)
        #     assert intraris.count() != 0
        # except:
        #     messages.success(request, ("Nu puteti termina o comanda daca nu ati inregistrat o intrarea!"))
        #     return redirect('home')
        # try:
        #     models.Iesire.objects.get(user=request.user, datetime__day=now.day)
        #     messages.success(request, ("Nu puteti termina o comanda daca ati inregistrat iesirea!"))
        #     return redirect('home')
        # except: pass
        try:
            models.Comanda.objects.get(datetime__year=now.year, numar_comanda=request.GET['nrcom'])
            messages.success(request, ("Aceasta comanda exista deja!"))
            return redirect('home')
        except: pass
        models.Comanda.objects.create(user=request.user, latitude=request.GET['lat'],
                                      longitude=request.GET['long'], datetime=now,
                                      nrcalcloc=1, text=utils.secureStr(request.GET['obs']),
                                      numar_comanda=request.GET['nrcom'], denumire=request.GET['den'])
        messages.success(request, ("Succes! Finalizarea a fost inregistrata!"))
    else:
        raise ValueError("POST in comand finish")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def comandaEdit(request):
    if request.method == "GET":
        if 'user' in request.GET:
            user = models.User.objects.get(username=request.GET['user'])
            now = datetime.datetime.fromisoformat(request.GET['datetime'])
            if request.GET['nr'] == "" or len(request.GET['nr']) == 0:
                messages.success(request, ("Numar comanda invalid!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            if str(request.GET['loc']).split(',').__len__() < 2:
                messages.success(request, ("Locatie invalida!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            try:
                models.Comanda.objects.get(datetime__year=now.year, numar_comanda=request.GET['nr'])
                messages.success(request, ("Numar comanda duplicat!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            except:
                pass
            coord = str(request.GET['loc']).split(',')
            models.Comanda.objects.create(user=user, numar_comanda=request.GET['nr'],
                                          denumire=request.GET['den'], text=request.GET['obs'], datetime=now,
                                          latitude=coord[0], longitude=coord[1])
            messages.success(request, ("Comanda a fost adaugata!"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        elif not 'datetime' in request.GET:
            now = utils.getTime()
            oldnr = request.GET['oldnr']
            try:
                old = models.Comanda.objects.get(user=request.user, datetime__date=now.date(), numar_comanda=oldnr)
            except:
                messages.success(request, ("Comanda veche nu a fost gasita!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            if 'nr' not in request.GET or len(request.GET['nr']) == 0:
                messages.success(request, ("Numar comanda invalid!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            if 'den' not in request.GET or len(request.GET['den']) == 0:
                messages.success(request, ("Denumire invalida!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            old.numar_comanda = request.GET['nr']
            old.denumire = request.GET['den']
            old.text = request.GET['obs']
            old.datetime = now
            old.save(force_update=True, update_fields=['numar_comanda', 'denumire', 'text', 'datetime'])
        else:
            now = datetime.datetime.fromisoformat(request.GET['datetime'])
            oldnr = request.GET['oldnr']

            try:
                old = models.Comanda.objects.get(datetime__date=now.date(), numar_comanda=oldnr)
            except:
                messages.success(request, ("Comanda veche nu a fost gasita!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            if 'nr' not in request.GET or len(request.GET['nr']) == 0:
                messages.success(request, ("Numar comanda invalid!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            if 'den' not in request.GET or len(request.GET['den']) == 0:
                messages.success(request, ("Denumire invalida!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            old.numar_comanda = request.GET['nr']
            old.denumire = request.GET['den']
            old.text = request.GET['obs']
            old.datetime = now
            old.latitude = str(request.GET['loc']).split(',')[0]
            old.longitude = str(request.GET['loc']).split(',')[1]
            old.save(force_update=True,
                     update_fields=['numar_comanda', 'denumire', 'text', 'datetime', 'latitude', 'longitude'])
    else:
        raise ValueError("POST in comand edit")
    messages.success(request, ("Comanda a fost actualizata!"))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def comandaCancel(request):
    if request.method == 'GET':
        now = utils.getTime()
        if not request.user.role in ("Manager", "Admin"):
            try:
                data = models.Comanda.objects.get(user=request.user, datetime__year=now.year,
                                                  numar_comanda=request.GET['nr'])
                data.delete()
            except:
                messages.success(request, ("Comanda nu a fost gasita!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            try:
                data = models.Comanda.objects.get(datetime__year=now.year, numar_comanda=request.GET['nr'])
                data.delete()
            except:
                messages.success(request, ("Comanda nu a fost gasita!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        raise ValueError("POST in cancel comanda")
    messages.success(request, ("Terminarea comenzii a fost anulata!"))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# endregion

# region Lucru

def lucruFinish(request):
    if request.method == "GET":
        now = utils.getTime()
        # try:
        #     models.Intrare.objects.get(user=request.user, datetime__day=now.day, datetime__lte=now)
        # except:
        #     messages.success(request, ("Nu puteti salva un lucru daca nu ati inregistrat intrarea!"))
        #     return redirect('home')
        # try:
        #     models.Iesire.objects.get(user=request.user, datetime__day=now.day)
        #     messages.success(request, ("Nu puteti salva un lucru daca ati inregistrat iesirea!"))
        #     return redirect('home')
        # except: pass
        if len(request.GET['den'])==0:
            messages.success(request, ("Nu ati introdus denumirea!"))
            return redirect('home')
        models.Lucru.objects.create(user=request.user, latitude=request.GET['lat'],
                                      longitude=request.GET['long'], datetime=now,
                                      nrcalcloc=1, text=utils.secureStr(request.GET['obs']),
                                      denumire=request.GET['den'])
        messages.success(request, ("Succes! Lucrul a fost inregistrat!"))
    else:
        raise ValueError("POST in lucru finish")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def lucruEdit(request):
    if request.method == "GET":
        if 'user' in request.GET:
            user = models.User.objects.get(username=request.GET['user'])
            now = datetime.datetime.fromisoformat(request.GET['datetime'])
            if str(request.GET['loc']).split(',').__len__() < 2:
                messages.success(request, ("Locatie invalida!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            if len(request.GET['den']) == 0:
                messages.success(request, ("Nu ati introdus denumirea!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            coord = str(request.GET['loc']).split(',')
            models.Lucru.objects.create(user=user, latitude=coord[0], longitude=coord[1],
                                          denumire=request.GET['den'], text=request.GET['obs'], datetime=now)
            messages.success(request, ("Lucrul a fost adaugat!"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        elif not 'datetime' in request.GET:
            now = utils.getTime()
            oldid = request.GET['id']
            try:
                old = models.Lucru.objects.get(pk=oldid)
            except:
                messages.success(request, ("Lucrul nu a fost gasit!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            if len(request.GET['den']) == 0:
                messages.success(request, ("Nu ati introdus denumirea!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            old.denumire = request.GET['den']
            old.text = request.GET['obs']
            old.datetime = now
            old.save(force_update=True, update_fields=['denumire', 'text', 'datetime'])
        else:
            now = datetime.datetime.fromisoformat(request.GET['datetime'])
            oldid = request.GET['id']
            try:
                old = models.Lucru.objects.get(pk=oldid)
            except:
                messages.success(request, ("Lucrul nu a fost gasit!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            if len(request.GET['den']) == 0:
                messages.success(request, ("Nu ati introdus denumirea!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            old.denumire = request.GET['den']
            old.text = request.GET['obs']
            old.datetime = now
            old.latitude = str(request.GET['loc']).split(',')[0]
            old.longitude = str(request.GET['loc']).split(',')[1]
            old.save(force_update=True,
                     update_fields=['denumire', 'text', 'datetime', 'latitude', 'longitude'])
    else:
        raise ValueError("POST in lucru edit")
    messages.success(request, ("Lucrul a fost actualizat!"))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def lucruCancel(request):
    if request.method == 'GET':
        now = utils.getTime()
        if not request.user.role in ("Manager", "Admin"):
            try:
                data = models.Lucru.objects.get(pk=request.GET['id'])
                data.delete()
            except:
                messages.success(request, ("Lucrul nu a fost gasit!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        else:
            try:
                data = models.Lucru.objects.get(pk=request.GET['id'])
                data.delete()
            except:
                messages.success(request, ("Lucrul nu a fost gasit!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    else:
        raise ValueError("POST in cancel lucru")
    messages.success(request, ("Lucrul a fost anulat!"))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# endregion

@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        setare = models.OwnSettings.objects.first()
        context.update(datalist_comanda=setare.getDataListComanda, datalist_lucru=setare.getDataListLucru)
        return context

# endregion

# region Activity

@method_decorator(login_required, name='dispatch')
class ActView(TemplateView):
    template_name = 'activityToday.html'

    def _getPeriod(self, **kwargs) -> tuple:
        pass

    def __proces_request_to_context(self, request, context: dict):
        context2 = {"stext": "", "selobs": "", "tobs": "i",
                    "scrit": "nume", "osin": "06:00", "osout": "22:00", "tiora": "in",
                    "ocrit": "nume", "oord": "cresc",
                    "prezenta": "pr"}
        for key in context2:
            if key in request.GET and len(request.GET[key]) != 0:
                context2[key] = request.GET[key]
        context.update(context2)

    def __create_filters(self, context: dict):
        filteruser = {}
        # filterin = {}
        # filterout = {}
        # filtercmd = {}
        if len(context["stext"]) > 0:
            if context["scrit"] == "nume": filteruser.update(nume__contains=context["stext"])
            elif context["scrit"] == "email": filteruser.update(email__contains=context["stext"])
            elif context["scrit"] == "tel": filteruser.update(telefon__startswith=context["stext"])
        ordlst = {}
        if context['oord'] == "desc": ordlst.update(reverse=True)
        if context["ocrit"] == "nume": ordlst.update(key=lambda r: (r.user.nume, r.datetime.date()))
        # elif context["ocrit"] == "datetimein": ordlst.update(key=lambda r: (r.datetime.date(), r.intrare_notnone.datetime.time()))
        # elif context["ocrit"] == "datetimeout": ordlst.update(key=lambda r: (r.datetime.date(), r.iesire_notnone.datetime.time()))
        # elif context["ocrit"] == "timein": ordlst.update(key=lambda r: (r.intrare_notnone.datetime.time(), r.user.nume))
        # elif context["ocrit"] == "timeout": ordlst.update(key=lambda r: (r.iesire_notnone.datetime.time(), r.user.nume))
        elif context["ocrit"] == "nrcom": ordlst.update(key=lambda r: (r.nrcomenzi, r.user.nume))
        elif context["ocrit"] == "nrin": ordlst.update(key=lambda r: (r.intrari.count(), r.user.nume))
        elif context["ocrit"] == "nrout": ordlst.update(key=lambda r: (r.iesiri.count(), r.user.nume))
        elif context["ocrit"] == "nrlucr": ordlst.update(key=lambda r: (r.lucrari.count(), r.user.nume))
        return filteruser, ordlst

    def get(self, request, *args, **kwargs):
        if request.user.role == "Angajat":
            if 'datein' in kwargs and 'dateout' in kwargs:
                if kwargs['datein'] != kwargs["dateout"]:
                    return redirect('actToday')
            context = self.get_context_data(**kwargs)
            datain = self._getPeriod(**context)[0].strftime("%d.%m.%Y")
            dataout = self._getPeriod(**context)[1].strftime("%d.%m.%Y")
            if datain == dataout:
                context.update(data=datain)
                if datain == utils.getTime().strftime("%d.%m.%Y"):
                    context.update(showcmdedit=True)
            else:
                context.update(datain=datain, dataout=dataout, data=None)
            return render(request, self.template_name, context)
        else:  # Manager, Admin
            # filtre
            context = {}
            self.__proces_request_to_context(request, context)
            filteruser, order = self.__create_filters(context)
            setari = models.OwnSettings.objects.first()

            # get data
            datetimein, datetimeout = self._getPeriod(**kwargs)
            harta = models.OwnSettings.objects.first().harta.adresa
            roluri_listate = ["Angajat", "Viewer", "Manager"]
            if request.user.role == "Admin": roluri_listate.append("Admin")
            tabledata = []
            for user in models.User.objects.filter(role__in=roluri_listate, **filteruser):
                for datetime in utils.rangeDays(datetimein, datetimeout):
                    row = RowDataActivity(user, datetime, setari.min_tolerated)
                    # skip condition not based on filters
                    if context["scrit"]=="numecmd" and str(context['stext']).casefold() not in row.numecomenzi.casefold() or \
                       context["scrit"]=="nrcmd" and not row.hasCmd(context["stext"]):
                        continue

                    # radio buttons - obs
                    # if context["selobs"]=="1":
                    #     if context["tobs"]=="i" and row.intrare_notnone.text == "": continue
                    #     elif context["tobs"]=="e" and row.iesire_notnone.text == "": continue
                    #     elif context["tobs"]=="ie" and (row.intrare_notnone.text == "" or row.iesire_notnone.text == ""): continue
                    #     else: pass

                    # radio buttons - prezenta
                    if context['prezenta']=="pr" and not row.absent or \
                       context['prezenta']=='abs' and row.absent:
                       # context['prezenta']=="iec" and not row.notAllDataCompleted or \
                       # context['prezenta']=="iei" and row.notAllDataCompleted and not row.noneDataCompleted:
                        tabledata.append(row)
            tabledata.sort(**order)
            context.update(tabledata=tabledata, harta=harta)
            return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context2 = {}

        datain, dataout = self._getPeriod(**context)
        user = self.request.user
        if 'ownuser' in kwargs: user = kwargs['ownuser']
        setari = models.OwnSettings.objects.first()
        harta = setari.harta.adresa
        context2['harta'] = harta

        if datain.date() == dataout.date():
            context['datetime'] = datain
            # In
            intrari = models.Intrare.objects.filter(user=user, datetime__gte=datain, datetime__lte=dataout).order_by("-datetime")
            context2['íntrari'] = intrari

            # Out
            iesiri = models.Iesire.objects.filter(user=user, datetime__gte=datain, datetime__lte=dataout).order_by("-datetime")
            context2['iesiri'] = iesiri

            # In Out
            inout = itertools.zip_longest(intrari, iesiri)
            context2["intrariiesiri"] = inout

            # Comenzi
            comenzi = models.Comanda.objects.filter(user=user, datetime__gte=datain, datetime__lte=dataout)
            context2['comenzi'] = comenzi
            context2['nrcomenzi'] = comenzi.count()

            # Lucrari
            lucrari = models.Lucru.objects.filter(user=user, datetime__gte=datain, datetime__lte=dataout)
            context2['lucrari'] = lucrari
            context2['nrlucrari'] = lucrari.count()
        else:
            tabledata = []
            for datetime in utils.rangeDays(datain, dataout):
                row = RowDataActivity(user, datetime, setari.min_tolerated)
                tabledata.append(row)
            tabledata.sort()
            context2['tabledata'] = tabledata
        context.update(context2)
        context.update(datalist_comanda=setari.getDataListComanda, datalist_lucru=setari.getDataListLucru)
        return context


# region Inherited change period

@method_decorator(login_required, name='dispatch')
class ActTodayView(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        date = utils.getTime().date()
        datetimein = datetime.datetime.combine(date, utils.datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(),
                                               tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(date, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(),
                                                tzinfo=pytz.timezone(settings.TIME_ZONE))
        return datetimein, datetimeout


@method_decorator(login_required, name='dispatch')
class ActYesterdayView(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        date = utils.getTime().date()
        date = utils.getPrevDay(date)
        datetimein = datetime.datetime.combine(date, datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(),
                                               tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(date, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(),
                                                tzinfo=pytz.timezone(settings.TIME_ZONE))
        return datetimein, datetimeout


@method_decorator(login_required, name='dispatch')
class Act2DaysAgoView(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        date = utils.getTime().date()
        date = utils.getPrevDay(date)
        date = utils.getPrevDay(date)
        datetimein = datetime.datetime.combine(date, datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(),
                                               tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(date, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(),
                                                tzinfo=pytz.timezone(settings.TIME_ZONE))
        return datetimein, datetimeout


@method_decorator(login_required, name='dispatch')
class ActLast3View(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        dateout = utils.getTime().date()
        datein = dateout
        for k in range(2): datein = utils.getPrevDay(datein)
        datetimein = datetime.datetime.combine(datein, datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(),
                                               tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(dateout, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(),
                                                tzinfo=pytz.timezone(settings.TIME_ZONE))
        return datetimein, datetimeout


@method_decorator(login_required, name='dispatch')
class ActLast7View(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        dateout = utils.getTime().date()
        datein = dateout
        while datein.strftime("%A") != "Monday": datein = utils.getPrevDay(datein)
        datetimein = datetime.datetime.combine(datein, datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(),
                                               tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(dateout, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(),
                                                tzinfo=pytz.timezone(settings.TIME_ZONE))
        return datetimein, datetimeout


@method_decorator(login_required, name='dispatch')
class ActFromPathView(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        datein = datetime.datetime.strptime(kwargs['datein'], "%d.%m.%Y")
        dateout = datetime.datetime.strptime(kwargs['dateout'], "%d.%m.%Y")
        datetimein = datetime.datetime.combine(datein, datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(),
                                               tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(dateout, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(),
                                                tzinfo=pytz.timezone(settings.TIME_ZONE))
        # datetimein = utils.getTime(datetimein)
        # datetimeout = utils.getTime(datetimeout)
        # print(datetimein, datetimeout)
        return datetimein, datetimeout


# endregion

def getperiod(request):
    if request.method == "POST":
        if request.user.role in ("Manager", "Admin"):
            date1 = datetime.datetime.fromisoformat(request.POST['date1'])
            date2 = datetime.datetime.fromisoformat(request.POST['date2'])
            if not date1 < date2:
                messages.success(request, ("Data inceputului este dupa data sfarsitului perioadei!"))
                return render(request, "getPeriod.html", {"now": utils.getTime()})
            return redirect('actFromPath', datein=date1.strftime("%d.%m.%Y"), dateout=date2.strftime("%d.%m.%Y"))
        else:
            date = datetime.datetime.fromisoformat(request.POST['date'])
            return redirect('actFromPath', datein=date.strftime("%d.%m.%Y"), dateout=date.strftime("%d.%m.%Y"))
    return render(request, "getPeriod.html", {"now": utils.getTime()})

def getperioduser(request):
    if request.method == "POST":
        date = datetime.datetime.fromisoformat(request.POST['date'])
        utilizator = request.POST['user']
        try:
            user = models.User.objects.get(nume=utilizator)
            return redirect('actUserFromPath', datein=date.strftime("%d.%m.%Y"), dateout=date.strftime("%d.%m.%Y"),
                            username=user.username)
        except:
            pass
        if utils.validTel(utilizator):
            try:
                user = models.User.objects.get(telefon=utilizator)
                return redirect('actUserFromPath', datein=date.strftime("%d.%m.%Y"), dateout=date.strftime("%d.%m.%Y"),
                                username=user.username)
            except:
                pass
        if "@" in str(utilizator):
            try:
                user = models.User.objects.get(email=utilizator)
                return redirect('actUserFromPath', datein=date.strftime("%d.%m.%Y"), dateout=date.strftime("%d.%m.%Y"),
                                username=user.username)
            except:
                pass
        try:
            user = models.User.objects.get(username=utilizator)
            return redirect('actUserFromPath', datein=date.strftime("%d.%m.%Y"), dateout=date.strftime("%d.%m.%Y"),
                            username=user.username)
        except:
            pass
        messages.success(request, ("Utilizatorul nu a fost gasit!"))
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
    return render(request, "getPeriodUser.html", {"users": models.User.objects.all(), "now": utils.getTime()})

@user_passes_test(lambda user: user.is_authenticated and user.role in ("Manager", "Admin"))
def getperioddelete(request):
    context = {"now": utils.getTime()}
    if request.method == "POST":
        try:
            date = request.POST['date']
            date = datetime.datetime.fromisoformat(date)
        except:
            messages.success(request, ("Data invalida!"))
            return render(request, 'getPeriodDelete.html', context)
        qs = models.Info.objects.filter(datetime__lte=date)
        messages.success(request, f"S-au sters {qs.count()} activitati!")
        qs.delete()
    return render(request, 'getPeriodDelete.html', context)


@method_decorator(login_required, name='dispatch')
class ActUserFromPathView(ActFromPathView):
    template_name = 'activityUser.html'

    def get(self, request, *args, **kwargs):
        if request.user.role in ("Manager", "Admin"):
            user = models.User.objects.get(username=kwargs['username'])
            if request.user.role == "Manager" and user.role == "Admin":
                messages.success(request, ("Nu aveti acces la activitatile acestui cont!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            kwargs['ownuser'] = user
            kwargs['user'] = user
            context = self.get_context_data(**kwargs)
            datetime = self._getPeriod(**context)[0]
            data = datetime.strftime("%d.%m.%Y")
            context.update(data=data, user=user, datetime=datetime)
            return render(request, self.template_name, context)
        else:
            messages.success(request, ("Nu aveti acces la activitatile acestui cont!"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    def post(self, request, *args, **kwargs):
        locin=None
        locout=None
        orain=None
        oraout=None
        datetimein=None
        datetimeout=None

        inid = request.POST['inid']
        outid = request.POST["outid"]

        def is_one_null(strora: str, strloc: str) -> bool:
            return len(strora) == 0 or len(strloc) == 0

        def is_both_null(strora: str, strloc: str) -> bool:
            return len(strora) == 0 and len(strloc) == 0

        try:
            # process data
            user = models.User.objects.get(username=kwargs['username'])
            data = datetime.datetime.strptime(kwargs['datein'], "%d.%m.%Y").date()
            strorain = str(request.POST['orain']).replace(" ", "").replace("-", "")
            stroraout = str(request.POST['oraout']).replace(" ", "").replace("-", "")
            if len(strorain) > 0:
                try:
                    orain = datetime.datetime.strptime(strorain, "%H:%M").time()
                    datetimein = datetime.datetime.combine(data, orain)
                except:
                    raise MyException("Format ora ajungere invalid!")
            if len(stroraout) > 0:
                try:
                    oraout = datetime.datetime.strptime(stroraout, "%H:%M").time()
                    datetimeout = datetime.datetime.combine(data, oraout)
                except:
                    raise MyException("Format ora plecare invalid!")
            strlocin = str(request.POST['locin']).replace(" ", "").replace("-", "")
            strlocout = str(request.POST['locout']).replace(" ", "").replace("-", "")
            if len(strlocin) > 0:
                try:
                    locin = strlocin.split(',')
                    assert (locin.__len__() == 2)
                except:
                    raise MyException("Format locatie ajungere invalid! Formatul este (lat,long)!")
            if len(strlocout) > 0:
                try:
                    locout = strlocout.split(',')
                    assert (locout.__len__() == 2)
                except:
                    raise MyException("Format locatie plecare invalid! Formatul este (lat,long)!")
            obsin = request.POST['obsin']
            obsout = request.POST['obsout']

            # intrare
            intrare = None
            try:
                intrare = models.Intrare.objects.get(pk=inid)
            except:
                if not is_one_null(strorain, strlocin):
                    #print("intrare is_notnull\n", locals())
                    models.Intrare.objects.create(user=user, latitude=locin[0], longitude=locin[1], datetime=datetimein,
                                                  text=obsin)
                    messages.success(request, ("Ajungerea a fost adaugata cu succes!"))
                else:
                    messages.success(request, ("Date insuficiente ajungere!"))
            if intrare is not None:
                if is_both_null(strorain, strlocin):
                    intrare.delete()
                    messages.success(request, ("Ajungerea a fost stearsa!"))
                elif is_one_null(strorain, strlocin):
                    if len(strlocin) > 0:  # locatia
                        report = ""
                        if intrare.latitude != locin[0] or intrare.longitude != locin[1]:
                            intrare.latitude = locin[0]
                            intrare.longitude = locin[1]
                            report+="Locatia, "
                        if intrare.text != obsin:
                            intrare.text = obsin
                            report+="Observatia, "
                        if report != "":
                            intrare.save(force_update=True, update_fields=['latitude', 'longitude', 'text'])
                            messages.success(request, (f"{report[:-2]} ajungerii s-a modificat cu succes!"))
                    else:  # ora
                        report = ""
                        if intrare.datetime != datetimein:
                            intrare.datetime = datetimein
                            report+="Timpul, "
                        if intrare.text != obsin:
                            intrare.text = obsin
                            report+="Observatia, "
                        if report!="":
                            intrare.save(force_update=True, update_fields=['datetime', 'text'])
                            messages.success(request, (f"{report[:-2]} ajungerii s-a modificat cu succes!"))
                else:
                    report=""
                    if intrare.latitude != locin[0] or intrare.longitude != locin[1]:
                        intrare.latitude = locin[0]
                        intrare.longitude = locin[1]
                        report += "Locatia, "
                    if intrare.datetime != datetimein:
                        intrare.datetime = datetimein
                        report += "Timpul, "
                    if intrare.text != obsin:
                        intrare.text = obsin
                        report += "Observatia, "
                    if report != "":
                        intrare.save(force_update=True, update_fields=['latitude', 'longitude', 'datetime', 'text'])
                        messages.success(request, (f"{report[:-2]} ajungerii s-a modificat cu succes!"))

            # iesire
            iesire = None
            try:
                iesire = models.Iesire.objects.get(pk=outid)
            except:
                if not is_one_null(stroraout, strlocout):
                    #print("iesire is_notnull\n", locals())
                    models.Iesire.objects.create(user=user, latitude=locout[0], longitude=locout[1],
                                                 datetime=datetimeout, text=obsout)
                    messages.success(request, ("Plecarea a fost adaugata cu succes!"))
                else:
                    messages.success(request, ("Date insuficiente plecare!"))
            if iesire is not None:
                report=""
                if is_both_null(stroraout, strlocout):
                    iesire.delete()
                    messages.success(request, ("Plecarea a fost stearsa!"))
                elif is_one_null(stroraout, strlocout):
                    if len(strlocout) > 0:  # locatia
                        if iesire.latitude != locout[0] or iesire.longitude != locout[1]:
                            iesire.latitude = locout[0]
                            iesire.longitude = locout[1]
                            report += "Locatia, "
                        if iesire.text != obsout:
                            iesire.text = obsout
                            report += "Observatia, "
                        if report!="":
                            iesire.save(force_update=True, update_fields=['latitude', 'longitude', 'text'])
                            messages.success(request, (f"{report[:-2]} plecarii s-a modificat cu succes!"))
                    else:  # ora
                        if iesire.datetime != datetimeout:
                            iesire.datetime = datetimeout
                            report += "Timpul, "
                        if iesire.text != obsout:
                            iesire.text = obsout
                            report += "Observatia, "
                        if report!="":
                            iesire.save(force_update=True, update_fields=['datetime', 'text'])
                            messages.success(request, (f"{report[:-2]} plecarii s-a modificat cu succes!"))
                else:
                    if iesire.latitude != locout[0] or iesire.longitude != locout[1]:
                        iesire.latitude = locout[0]
                        iesire.longitude = locout[1]
                        report+="Locatia, "
                    if iesire.datetime != datetimeout:
                        iesire.datetime = datetimeout
                        report += "Timpul, "
                    if iesire.text != obsout:
                        iesire.text = obsout
                        report += "Observatia, "
                    if report!="":
                        iesire.save(force_update=True, update_fields=['latitude', 'longitude', 'datetime', 'text'])
                        messages.success(request, (f"{report[:-2]} plecarii s-a modificat cu succes!"))
        except MyException as e:
            messages.success(request, (e.args[0]))
        except Exception as ex:
            messages.success(request, ("Eroare!"))
        finally: pass
        return HttpResponseRedirect(self.request.path_info)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        setare = models.OwnSettings.objects.first()
        context.update(show_edit=True, nrrecalcpoz=setare.nrrecalcpoz + 1)
        context.update(datalist_comanda=setare.getDataListComanda, datalist_lucru=setare.getDataListLucru)
        context.update(showinoutsupl=True)
        return context


# endregion

#region Separated Activity

class BaseActivityView(TemplateView):
    template_name = "sepAct.html"
    titlu = "Intrare/Iesire/Comenzi"
    model = models.Info

    def _proces_request_to_context(self, request, context: dict):
        context2 = {"stext": "", "showday": "",
                    "scrit": "nume",
                    "ocrit": "nume", "oord": "cresc",
                    "prezenta": "pr"}
        for key in context2:
            if key in request.GET and len(request.GET[key]) != 0:
                context2[key] = request.GET[key]
        for datekey in ("date1", "date2"):
            if datekey in request.GET:
                data = datetime.datetime.fromisoformat(request.GET[datekey])
                #print(data, datekey[-1])
                context2[f"datetime{datekey[-1]}"] = data
        context.update(context2)

    def _create_filters(self, context: dict):
        filterdct = {}
        #models.Comanda.objects.filter(user=)
        if 'user' in context:
            filterdct.update(user=context['user'])
        elif len(context["stext"]) > 0:
            if context["scrit"] == "nume":
                filterdct.update(user__nume__contains=context["stext"])
            elif context["scrit"] == "email":
                filterdct.update(user__email__contains=context["stext"])
            elif context["scrit"] == "tel":
                filterdct.update(user__telefon__startswith=context["stext"])
            elif context["scrit"] == "obs":
                filterdct.update(text__contains=context["stext"])
            # comanda
            elif context["scrit"] == "numecmd":
                filterdct.update(denumire__contains=context["stext"])
            elif context["scrit"] == "nrcmd":
                filterdct.update(numar_comanda__startswith=context["stext"])
            # lucrare
            elif context["scrit"] == "den":
                filterdct.update(denumire__contains=context["stext"])

        filterdct.update(datetime__gte=context["datetime1"], datetime__lte=context["datetime2"])
        return filterdct

    def _order_query(self, context: dict, query):
        supl = ""
        rez = None
        if context['oord'] == "desc": supl = "-"
        if context["ocrit"] == "nume":
            rez = query.order_by(supl+'user__nume', 'datetime__date')
            # ordlst.update(key=lambda r: (r.user.nume, r.datetime.date()))
        elif context["ocrit"] == "data":
            rez = query.order_by(supl+'datetime__date', 'user__nume')
            # ordlst.update(key=lambda r: (r.datetime.date(), r.user.nume))
        elif context["ocrit"] == "ora":
            rez = query.order_by(supl+'datetime__time', 'user__nume')
            # ordlst.update(key=lambda r: (r.datetime.time(), r.user.nume))
        if rez is None:  # dupa distanta
            rez = list(query)
            desc = supl == "-"
            rez.sort(key=lambda info: (utils.getTime(info), info.user.nume), reverse=desc)
        return rez

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        self._proces_request_to_context(request, context)
        filterdct = self._create_filters(context)
        tabledata = self.model.objects.filter(**filterdct)
        tabledata = self._order_query(context, tabledata)
        context.update(tabledata=tabledata)
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        date = utils.getTime().date()
        if 'date' in kwargs:
            date = datetime.datetime.strptime(kwargs['date'], "%d.%m.%Y")
        user = None
        if 'username' in kwargs:
            user = models.User.objects.get(username=kwargs['username'])
        time1 = datetime.datetime.strptime("00:00:00", "%H:%M:%S").time()
        time2 = datetime.datetime.strptime("23:59:00", "%H:%M:%S").time()
        datetime1 = datetime.datetime.combine(date, time1, tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetime2 = datetime.datetime.combine(date, time2, tzinfo=pytz.timezone(settings.TIME_ZONE))
        context.update(titlu=self.titlu, datetime1=datetime1, datetime2=datetime2)
        if user is not None: context.update(user=user)
        harta = models.OwnSettings.objects.first().harta.adresa
        context.update(harta=harta)
        return context

#region Inherited change model

class IntrareActivity(BaseActivityView):
    titlu = "Ajungeri"
    model = models.Intrare

class IesireActivity(BaseActivityView):
    titlu = "Plecari"
    model = models.Iesire

class ComandaActivity(BaseActivityView):
    template_name = 'comenzi.html'
    titlu = "Comenzi"
    model = models.Comanda

class LucruActivity(BaseActivityView):
    template_name = 'lucrari.html'
    titlu = "Lucrari"
    model = models.Lucru

#endregion

#endregion

# region Users

@user_passes_test(lambda user: user.is_authenticated and user.role in ("Manager", "Admin"))
def adduser(request):
    if request.method == 'POST':
        username = request.POST['user']
        nume = request.POST['nume']
        email = request.POST['email']
        tel = request.POST['tel']
        pwd = request.POST['pwd']
        role = request.POST['role']
        try:
            models.User.objects.get(username=username)
            messages.success(request, ("Numele de utilizator exista deja! Incercati altul sau regenerati-l."))
            return redirect('adduser')
        except:
            pass
        try:
            models.User.objects.get(nume=nume)
            messages.success(request, ("Numele exista deja!"))
            return redirect('adduser')
        except:
            pass
        models.User.objects.create(username=username, nume=nume, email=email, telefon=tel, password=pwd, role=role, is_active=True)
        messages.success(request, ("Contul a fost creeat cu succes!"))
        return redirect('detaliiuser', username=username)
    return render(request, 'adduser.html', {})


@user_passes_test(lambda user: user.is_authenticated and user.role in ("Manager", "Admin"))
def deleteuser(request, username):
    try:
        data = models.User.objects.get(username=username)
    except:
        messages.success(request, ("Utilizatorul nu a fost gasit!"))
        return HttpResponseRedirect(request.path_info)
    if data.role in ("Manager", "Admin") and request.user.role == "Manager":
        messages.success(request, ("Nu puteti sterge acest cont!"))
    else:
        data.delete()
        messages.success(request, ("Acest cont a fost sters!"))
    return redirect('utilizatori')


def detalii(request, username=None):
    user = request.user
    if username is not None and (user.role == "Manager" or user.role == "Admin"):
        newuser = models.User.objects.get(username=username)
        if user.role == "Manager" and newuser.role == "Admin":
            messages.success(request, ("Nu aveti acces la contul de administrator de pe un cont de manager!"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        if user.role == "Manager" and request.method == 'POST' and request.POST['role'] == "Admin":
            messages.success(request, ("Nu puteti creea un administrator de pe un cont de manager!"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
        user = newuser
    elif username is not None:
        messages.success(request, ("Nu puteti vizualiza un alt cont daca nu sunteti cel putin manager!"))
        return redirect('detalii')
    if request.method == 'POST':
        if not utils.isEqual(user, request):
            if utils.validAccountModif(user, request):
                user.username = request.POST['user']
                user.email = request.POST['email']
                user.telefon = request.POST['tel']
                user.password = request.POST['pwd']
                if username is not None and (request.user.role == "Manager" or request.user.role == "Admin"):
                    user.nume = request.POST['nume']
                    user.role = request.POST['role']
                    user.groups.clear()
                    group = Group.objects.get(name=user.role)
                    user.groups.add(group)
                    user.save(force_update=True)
                else:
                    user.save(force_update=True)
                    login(request, user)
                messages.success(request, ("Modificarile au fost efectuate!"))
        else:
            messages.success(request, ("Nu exista nici o modificare!"))
    return render(request, 'detalii.html', {"userdata": user})


@method_decorator(login_required, name='dispatch')
class Utilizatori(TemplateView):
    template_name = 'users.html'

    def get(self, request, *args, **kwargs):
        if request.user.role in ("Manager", "Admin"):
            try:
                searchtext = request.GET['search']
            except:
                searchtext = ""
            try:
                crit = request.GET['crit']
            except:
                crit = "nume"
            context = {'ch1': True, 'ch2': True, 'ch3': True, 'now': utils.getTime(), 'stext': searchtext}
            asocs = {"ch1": "angajat", "ch2": "manager", "ch3": "admin", }
            roluri = []
            isnothing = searchtext.__len__() == 0
            for i in range(1, 4):
                ch = f"ch{i}"
                if asocs[ch] not in request.GET:
                    context[ch] = False
                isnothing = isnothing and not context[ch]
                if context[ch] == True:
                    roluri.append(asocs[ch][0].capitalize() + asocs[ch][1:])

            if isnothing:
                users = models.User.objects.all().order_by('nume')
            else:
                searchcontext = {}
                if searchtext != "":
                    if crit == "nume":
                        searchcontext.update(nume__contains=searchtext)
                    elif crit == "username":
                        searchcontext.update(username__startswith=searchtext)
                    elif crit == "tel":
                        searchcontext.update(telefon__startswith=searchtext)
                    elif crit == "email":
                        searchcontext.update(email__contains=searchtext)
                    users = models.User.objects.filter(role__in=roluri, **searchcontext).order_by("nume")
                else:
                    users = models.User.objects.filter(role__in=roluri).order_by("nume")
            context.update(users=users, isnothing=isnothing, crit=crit)
            return render(request, "users.html", context)
        else:
            messages.success(request, ("Nu sunteti autorizat sa vizualizati alte conturi!"))
            return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

# endregion

#region Setari

@method_decorator(login_required, name='dispatch')
class Setari(TemplateView):
    template_name = 'setari.html'

    def __validate_post_setare(self, request):
        keys = ("nrrecalcpoz", "secafterrecalc", "disterror", "harta", "progr", "dlcmd", "dllcr")
        for key in keys:
            if not key in request.POST:
                messages.success(request, ("Date insuficiente!"))
                return None
        nr = int(request.POST[keys[0]])
        if nr < 1 or nr > 10:
            messages.success(request, ("Numar de localizari invalid!"))
            return None
        try: sec = int(request.POST[keys[1]])
        except: sec = int(float(request.POST[keys[1]]))
        if sec < 0 or sec > 2000:
            messages.success(request, ("Numar de secunde invalid!"))
            return None
        dist = float(request.POST[keys[2]])
        if dist < 0 or dist > 1000:
            messages.success(request, ("Distanta invalida!"))
            return None
        # try: mintol = int(request.POST[keys[3]])
        # except: mintol = int(float(request.POST[keys[3]]))
        # if mintol < 0 or mintol >= 1440:
        #     messages.success(request, ("Numar de minute tolerate invalid!"))
        #     return None
        mintolskip = -1
        hartaid = request.POST[keys[4 + mintolskip]]
        harta = None
        try: harta = models.Harta.objects.get(pk=hartaid)
        except:
            messages.success(request, ("Harta invalida!"))
            return None
        progr = request.POST.getlist(keys[5+ mintolskip])
        if len(progr) == 0:
            messages.success(request, ("Program invalid!"))
            return None
        progr = " ".join(progr)
        dlcmd = str(request.POST[keys[6+ mintolskip]])
        dllcr = str(request.POST[keys[7+ mintolskip]])
        vals = (nr, sec, dist, harta, progr, dlcmd, dllcr)
        context = {keys[i]: vals[i] for i, _ in enumerate(keys)}
        return context

    def __validate_post_harta(self, request):
        keys = ("id", "nume", "adr")
        for key in keys:
            if not key in request.POST:
                messages.success(request, ("Date insuficiente!"))
                return None
        nume = request.POST['nume']
        if len(nume) == 0:
            messages.success(request, ("Numa invalid!"))
            return None
        adresa = request.POST['adr']
        if len(adresa) == 0:
            messages.success(request, ("Adresa invalida!"))
            return None
        id = int(request.POST['id'])
        try: models.Harta.objects.get(pk=id)
        except:
            messages.success(request, ("Harta invalida!"))
            return None
        return dict(zip(keys, (id, nume, adresa)))

    def __validate_post_hartaadd(self, request):
        keys = ("nume", "adr")
        for key in keys:
            if not key in request.POST:
                messages.success(request, ("Date insuficiente!"))
                return None
        nume = request.POST['nume']
        if len(nume) == 0:
            messages.success(request, ("Numa invalid!"))
            return None
        adresa = request.POST['adr']
        if len(adresa) == 0:
            messages.success(request, ("Adresa invalida!"))
            return None
        return dict(zip(keys, (nume, adresa)))

    def __validate_post_forma(self, request):
        keys = ("id", "nume", "pozc", "pozp")
        for key in keys:
            if not key in request.POST:
                messages.success(request, ("Date insuficiente!"))
                return None
        nume = request.POST['nume']
        if len(nume) == 0:
            messages.success(request, ("Numa invalid!"))
            return None
        pozc = request.POST['pozc']
        if not utils.validLoc(pozc):
            messages.success(request, ("Pozitie centru invalida!"))
            return None
        pozp = request.POST['pozp']
        if not utils.validLoc(pozp):
            messages.success(request, ("Pozitie punct invalida!"))
            return None
        id = int(request.POST['id'])
        try: models.Forma.objects.get(pk=id)
        except:
            messages.success(request, ("Forma invalida!"))
            return None
        return dict(zip(keys, (id, nume, pozc, pozp)))

    def __validate_post_formaadd(self, request):
        keys = ("nume", "pozc", "pozp")
        for key in keys:
            if not key in request.POST:
                messages.success(request, ("Date insuficiente!"))
                return None
        nume = request.POST['nume']
        if len(nume) == 0:
            messages.success(request, ("Numa invalid!"))
            return None
        pozc = request.POST['pozc']
        if not utils.validLoc(pozc):
            messages.success(request, ("Pozitie centru invalida!"))
            return None
        pozp = request.POST['pozp']
        if not utils.validLoc(pozp):
            messages.success(request, ("Pozitie punct invalida!"))
            return None
        return dict(zip(keys, (nume, pozc, pozp)))

    def post(self, request, *args, **kwargs):
        if request.POST['type'] == "setare":
            context = self.__validate_post_setare(request)
            if context is not None:
                seatre = models.OwnSettings.objects.first()
                seatre.nrrecalcpoz = context['nrrecalcpoz']
                seatre.secafterrecalc = context['secafterrecalc']
                seatre.disterror = context['disterror']
                #seatre.min_tolerated = context['mintol']
                seatre.program = context['progr']
                seatre.harta = context['harta']
                seatre.datalist_comanda = context['dlcmd']
                seatre.datalist_lucru = context['dllcr']
                seatre.save(force_update=True)
                messages.success(request, ("Setare modificata cu succes!"))
        elif request.POST['type'] == 'harta':
            context = self.__validate_post_harta(request)
            if context is not None:
                harta = models.Harta.objects.get(pk=context['id'])
                harta.nume = context['nume']
                harta.adresa = context['adr']
                harta.save(force_update=True)
                messages.success(request, ("Harta modificata cu succes!"))
        elif request.POST['type'] == 'hartaadd':
            context = self.__validate_post_hartaadd(request)
            if context is not None:
                models.Harta.objects.create(nume=context['nume'], adresa=context['adr'])
                messages.success(request, (f"Harta {context['nume']} adaugata cu succes!"))
        elif request.POST['type'] == 'forma':
            context = self.__validate_post_forma(request)
            if context is not None:
                forma = models.Forma.objects.get(pk=context['id'])
                forma.nume = context['nume']
                rowc = str(context['pozc']).replace(" ", "").replace(",", ' ')
                rowp = str(context['pozp']).replace(" ", "").replace(",", ' ')
                forma.puncte = f"{rowc}\n{rowp}"
                forma.save(force_update=True)
                messages.success(request, ("Aria modificata cu succes!"))
        elif request.POST['type'] == 'formaadd':
            context = self.__validate_post_formaadd(request)
            if context is not None:
                rowc = str(context['pozc']).replace(" ", "").replace(",", ' ')
                rowp = str(context['pozp']).replace(" ", "").replace(",", ' ')
                models.Forma.objects.create(nume=context['nume'], puncte=f"{rowc}\n{rowp}")
                messages.success(request, (f"Aria {context['nume']} adaugata cu succes!"))
        return redirect('setari')

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        # if 'modif' in request.GET: context.update(modif=True)
        return render(request, self.template_name, context)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        setare = models.OwnSettings.objects.first()
        arii = models.Forma.objects.all()
        harti = models.Harta.objects.all()
        context.update(setare=setare, arii=arii, harti=harti)
        return context

@user_passes_test(lambda user: user.is_authenticated and user.role in ("Manager", "Admin"))
def stergeharta(request, hid):
    try:
        harta = models.Harta.objects.get(pk=hid)
        nume = harta.nume
        setare = models.OwnSettings.objects.first()
        if harta.id == setare.harta.id:
            messages.success(request, (f"Harta {nume} este setata ca fiind harta curenta! Va rugam sa selectati alta harta daca doriti sa o stergeti pe aceasta!"))
            return redirect('setari')
        harta.delete()
        messages.success(request, (f"Harta {nume} a fost stearsa!"))
    except Exception as ex:
        messages.success(request, ("Eroare!"))
    return redirect('setari')

@user_passes_test(lambda user: user.is_authenticated and user.role in ("Manager", "Admin"))
def stergeforma(request, fid):
    try:
        forma = models.Forma.objects.get(pk=fid)
        nume = forma.nume
        forma.delete()
        messages.success(request, (f"Aria {nume} a fost stearsa!"))
    except:
        messages.success(request, ("Eroare!"))
    return redirect('setari')

#endregion

#region About

def about(request):
    context = {}
    setare=models.OwnSettings.objects.first()
    carousellogin = Carousel()
    carousellogin.addItem("https://i.ibb.co/3k3RYQZ/login.png")
    carousellogin.addItem("https://i.ibb.co/WvjBx2D/loginnume.png")
    carousellogin.addItem("https://i.ibb.co/fXyKMNr/loginemail.png")
    carousellogin.addItem("https://i.ibb.co/xGKyp3R/logintel.png")
    carousellogin.addItem("https://i.ibb.co/sH8nbXT/loginusername.png")
    context.update(carousellogin=carousellogin, setare=setare)
    if request.user.role == "Angajat":
        return render(request, 'about.html', context)


    return render(request, 'aboutManager.html', context)
#endregion