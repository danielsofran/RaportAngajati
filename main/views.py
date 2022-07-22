import datetime

import pytz
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

import main.templatetags.mytags
from . import models
from . import utils
from siteReport import settings
from .viewmodels import *

# Create your views here.

# region Login
def login_user(request):
    if(request.method == "POST"):
        username = request.POST['username']
        password = request.POST['password']

        user = None

        try: user = get_user_model().objects.get(username=username, password=password)
        except: pass

        if user is not None:
            login(request, user)
            return redirect('home')

        try: user = get_user_model().objects.get(email=username, password=password)
        except: pass

        if user is not None:
            login(request, user)
            return redirect('home')

        try: user = get_user_model().objects.get(telefon=username, password=password)
        except: pass

        if user is not None:
            login(request, user)
            return redirect('home')

        messages.success(request, ("Date de autentificare invalide!"))
        return HttpResponseRedirect(request.path_info)

    else:
        return render(request, 'login.html', {})

def logout_user(request):
    logout(request)
    return redirect('mylogin')

#endregion

#region Home

#region Come Left

def come(request):
    if request.method == 'GET':
        now = utils.getTime()
        SEC_RECALC_AFTER = 60
        NR_RECALC_POZ = 3
        try:
            setare = models.OwnSettings.objects.all()[0]
            SEC_RECALC_AFTER = setare.secafterrecalc
            NR_RECALC_POZ = setare.nrrecalcpoz
        except:
            print("Nu exista setari")
        try:
            data = models.Iesire.objects.get(user=request.user, datetime__day=now.day)
            messages.success(request, ("Nu puteti inregistra intrarea din moment ce iesirea este salvata!"))
            return redirect('home')
        except: pass
        try:
            data = models.Intrare.objects.get(user=request.user, datetime__day=now.day)
            messages.success(request, ("Momentul intrarii a fost deja inregistrat!\nVa rugam sa il stergeti daca a fost adaugat din greseala!"))
            return redirect('home')
        except:
            models.Intrare.objects.create(user=request.user, latitude=request.GET['lat'], longitude=request.GET['long'], datetime=now, nrcalcloc=1, text=utils.secureStr(request.GET['obs']))
            messages.success(request, ("Succes!"))
            messages.success(request, (f"Daca considerati ca locatia nu este precisa(erori de peste 10-20m), puteti sa folositi butonul relocare de maxim {NR_RECALC_POZ} ori.\nTimpul limita pentru o relocare este de un minut dupa ultima relocare."))
    else: print("POST in come")
    return redirect('home')

def cancel_come(request):
    now = utils.getTime()
    try:
        data = models.Iesire.objects.get(user=request.user, datetime__day=now.day)
        messages.success(request, ("Nu puteti anula intrarea daca ati inregistrat iesirea!"))
        return redirect('home')
    except: pass
    try: data = models.Intrare.objects.get(user=request.user, datetime__day=now.day)
    except:
        messages.success(request, ("Momentul intrarii nu a fost inregistrat!"))
        return redirect('home')
    data.delete()
    messages.success(request, ("Momentul intrarii a fost sters!"))
    return redirect('home')

def recalc_come(request):
    SEC_RECALC_AFTER = 60
    NR_RECALC_POZ = 3
    try:
        setare = models.OwnSettings.objects.all()[0]
        SEC_RECALC_AFTER = setare.secafterrecalc
        NR_RECALC_POZ = setare.nrrecalcpoz
    except: print("Nu exista setari")
    try:
        now = utils.getTime()
        data = models.Intrare.objects.get(user=request.user, datetime__day=now.day)
        if (now-utils.getTime(data)).seconds > SEC_RECALC_AFTER:
            raise ValueError("Timpul pentru relocare a expirat!")
        nr = data.nrcalcloc
        if nr <= NR_RECALC_POZ:
            data.nrcalcloc = data.nrcalcloc + 1
            data.latitude = request.GET['lat']
            data.longitude = request.GET['long']
            data.save(update_fields=['latitude', 'longitude', 'nrcalcloc'])
            messages.success(request, (f"Locatie actualizata! Mai aveti {NR_RECALC_POZ +1 - data.nrcalcloc} relocari."))
        else: messages.success(request, (f"Nu mai aveti relocari disponibile."))
    except: messages.success(request, ("Timpul pentru relocare a expirat!"))
    return redirect('actToday')

def left(request):
    now = utils.getTime()
    SEC_RECALC_AFTER = 60
    NR_RECALC_POZ = 3
    try:
        setare = models.OwnSettings.objects.all()[0]
        SEC_RECALC_AFTER = setare.secafterrecalc
        NR_RECALC_POZ = setare.nrrecalcpoz
    except:
        print("Nu exista setari")
    if models.Intrare.objects.filter(user=request.user, datetime__day=now.day).__len__() <= 0:
        messages.success(request, (f"Nu puteti parasi inainte sa intrati!"))
        return redirect('home')
    try:
        data = models.Iesire.objects.get(user=request.user, datetime__day=now.day)
        messages.success(request, ("Momentul iesirii a fost deja inregistrat!\nVa rugam sa il stergeti daca a fost adaugat din greseala!"))
        return redirect('home')
    except:
        models.Iesire.objects.create(user=request.user, latitude=request.GET['lat'], longitude=request.GET['long'], datetime=now, nrcalcloc=1, text=utils.secureStr(request.GET['obs']))
        messages.success(request, ("Succes!"))
        messages.success(request, (f"Daca considerati ca locatia nu este precisa(erori de peste 10-20m), puteti sa folositi butonul relocare de maxim {NR_RECALC_POZ} ori.\nTimpul limita pentru o relocare este de un minut dupa ultima relocare."))
    return redirect('home')

def cancel_left(request):
    now = utils.getTime()
    try:
        models.Intrare.objects.get(user=request.user, datetime__day=now.day)
    except:
        messages.success(request, (f"Nu puteti parasi inainte sa intrati!"))
        return redirect('home')
    try: data = models.Iesire.objects.get(user=request.user, datetime__day=now.day)
    except:
        messages.success(request, ("Momentul iesirii nu a fost inregistrat!"))
        return redirect('home')
    data.delete()
    messages.success(request, ("Momentul iesirii a fost sters!"))
    return redirect('home')

def recalc_left(request):
    now = utils.getTime()
    SEC_RECALC_AFTER = 60
    NR_RECALC_POZ = 3
    try:
        setare = models.OwnSettings.objects.all()[0]
        SEC_RECALC_AFTER = setare.secafterrecalc
        NR_RECALC_POZ = setare.nrrecalcpoz
    except:
        print("Nu exista setari")
    try:
        models.Intrare.objects.get(user=request.user, datetime__day=now.day)
    except:
        messages.success(request, (f"Nu puteti parasi inainte sa intrati!"))
        return redirect('actToday')
    try:
        data = models.Iesire.objects.get(user=request.user, datetime__day=now.day)
        if (now-utils.getTime(data)).seconds > SEC_RECALC_AFTER:
            raise ValueError("Timpul pentru relocare a expirat!")
        nr = data.nrcalcloc
        if nr <= NR_RECALC_POZ:
            data.nrcalcloc = data.nrcalcloc + 1
            data.latitude = request.GET['lat']
            data.longitude = request.GET['long']
            data.save(update_fields=['latitude', 'longitude', 'nrcalcloc'])
            messages.success(request, (f"Locatie actualizata! Mai aveti {NR_RECALC_POZ +1 - data.nrcalcloc} relocari."))
        else: messages.success(request, (f"Nu mai aveti relocari disponibile."))
    except: messages.success(request, ("Nu exista o locatie initiala ce poate fi actualizata"))
    return redirect('actToday')

#endregion

#region Comanda

def comandaFinish(request):
    if request.method == "GET":
        now = utils.getTime()
        try: models.Intrare.objects.get(user=request.user, datetime__day=now.day, datetime__lte=now)
        except:
            messages.success(request, ("Nu puteti termina o comanda daca nu ati inregistrat intrarea!"))
            return redirect('home')
        try:
            models.Iesire.objects.get(user=request.user, datetime__day=now.day)
            messages.success(request, ("Nu puteti termina o comanda daca ati inregistrat iesirea!"))
            return redirect('home')
        except: pass
        try:
            models.Comanda.objects.get(numar_comanda=request.GET['nrcom'])
            messages.success(request, ("Aceasta comanda exista deja!"))
            return redirect('home')
        except:
            models.Comanda.objects.create(user=request.user, latitude=request.GET['lat'],
                                          longitude=request.GET['long'], datetime=now,
                                          nrcalcloc=1, text=utils.secureStr(request.GET['obs']), numar_comanda=request.GET['nrcom'], denumire=request.GET['den'])
            messages.success(request, ("Succes! Finalizarea a fost inregistrata!"))
    else:
        raise ValueError("POST in comand finish")
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def comandaEdit(request):
    if request.method == "GET":
        if not 'datetime' in request.GET:
            now = utils.getTime()
            oldnr = request.GET['oldnr']
            try: old = models.Comanda.objects.get(user=request.user, datetime__day=now.day, datetime__year=now.year, numar_comanda=oldnr)
            except:
                messages.success(request, ("Comanda veche nu a fost gasita!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            old.numar_comanda = request.GET['nr']
            old.denumire = request.GET['den']
            old.text = request.GET['obs']
            old.datetime = now
            old.save(force_update=True, update_fields=['numar_comanda', 'denumire', 'text', 'datetime'])
        else:
            now = datetime.datetime.fromisoformat(request.GET['datetime'])
            oldnr = request.GET['oldnr']

            try: old = models.Comanda.objects.get(datetime__day=now.day, datetime__year=now.year, numar_comanda=oldnr)
            except:
                messages.success(request, ("Comanda veche nu a fost gasita!"))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))
            old.numar_comanda = request.GET['nr']
            old.denumire = request.GET['den']
            old.text = request.GET['obs']
            old.datetime = now
            old.latitude = str(request.GET['loc']).split(',')[0]
            old.longitude = str(request.GET['loc']).split(',')[1]
            old.save(force_update=True, update_fields=['numar_comanda', 'denumire', 'text', 'datetime', 'latitude', 'longitude'])
    else: raise ValueError("POST in comand edit")
    messages.success(request, ("Comanda a fost actualizata!"))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

def comandaCancel(request):
    if request.method == 'GET':
        now = utils.getTime()
        if not request.user.role in ("Manager", "Admin"):
            try:
                data = models.Comanda.objects.get(user=request.user, datetime__year=now.year, numar_comanda=request.GET['nr'])
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
    else: raise ValueError("POST in cancel comanda")
    messages.success(request, ("Terminarea comenzii a fost anulata!"))
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

#endregion

@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    template_name = 'home.html'

#region Activity

@method_decorator(login_required, name='dispatch')
class ActView(TemplateView):
    template_name = 'activityToday.html'

    def _getPeriod(self, **kwargs) -> tuple:
        pass

    def get(self, request, *args, **kwargs):
        if request.user.role == "Angajat":
            if 'datein' in kwargs and 'dateout' in kwargs:
                if kwargs['datein'] != kwargs["dateout"]:
                    return redirect('actToday')
            context = self.get_context_data(**kwargs)
            datain = self._getPeriod(**context)[0].strftime("%d.%m.%Y")
            dataout = self._getPeriod(**context)[1].strftime("%d.%m.%Y")
            if datain == dataout: context.update(data=datain)
            else: context.update(datain=datain, dataout=dataout, data=None)
            return render(request, self.template_name, context)
        else: # Manager, Admin
            datetimein, datetimeout = self._getPeriod(**kwargs)
            harta = models.OwnSettings.objects.all()[0].harta.adresa
            roluri_listate = ["Angajat", "Viewer"]
            if request.user.role == "Admin":
                roluri_listate.append("Manager")
            tabledata = []
            for user in models.User.objects.filter(role__in=roluri_listate):
                for datetime in utils.rangeDays(datetimein, datetimeout):
                    row = RowDataActiviy(user, datetime)
                    tabledata.append(row)
            tabledata.sort()
            return render(request, self.template_name, {"tabledata": tabledata, "harta": harta})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context2 = {}

        datain, dataout = self._getPeriod(**context)
        user = self.request.user
        if 'ownuser' in kwargs: user = kwargs['ownuser']
        harta = models.OwnSettings.objects.all()[0].harta.adresa
        context2['harta'] = harta

        if datain.date() == dataout.date():
            # In
            try:
                gasit = models.Intrare.objects.get(user=user, datetime__gte=datain, datetime__lte=dataout)
                context2['oraIn'] = utils.getTime(gasit).strftime("%H:%M")
                context2['locIn'] = f"{gasit.latitude},{gasit.longitude}"
                context2['locStrIn'] = utils.locStr(gasit)
                context2['obsIn'] = gasit.text
            except:
                context2['oraIn'] = "-"
                context2['locIn'] = "-"
                context2['locStrIn'] = "-"
                context2['obsIn'] = ""

            # Out
            try:
                gasit = models.Iesire.objects.get(user=user, datetime__gte=datain, datetime__lte=dataout)
                context2['oraOut'] = utils.getTime(gasit).strftime("%H:%M")
                context2['locOut'] = f"{gasit.latitude},{gasit.longitude}"
                context2['locStrOut'] = utils.locStr(gasit)
                context2['obsOut'] = gasit.text
            except:
                context2['oraOut'] = "-"
                context2['locOut'] = "-"
                context2['locStrOut'] = "-"
                context2['obsOut'] = ""

            #Comenzi
            try:
                comenzi = models.Comanda.objects.filter(user=user, datetime__gte=datain, datetime__lte=dataout)
                context2['comenzi'] = comenzi
            except:
                context2['comenzi'] = []
        else:
            tabledata = []
            for datetime in utils.rangeDays(datain, dataout):
                row = RowDataActiviy(user, datetime)
                tabledata.append(row)
            tabledata.sort()
            context2['tabledata'] = tabledata
        context.update(context2)
        return context

@method_decorator(login_required, name='dispatch')
class ActTodayView(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        date = utils.getTime().date()
        datetimein = datetime.datetime.combine(date, utils.datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(date, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        return datetimein, datetimeout

@method_decorator(login_required, name='dispatch')
class ActYesterdayView(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        date = utils.getTime().date()
        date = utils.getPrevDay(date)
        datetimein = datetime.datetime.combine(date, datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(date, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        return datetimein, datetimeout

@method_decorator(login_required, name='dispatch')
class Act2DaysAgoView(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        date = utils.getTime().date()
        date = utils.getPrevDay(date)
        date = utils.getPrevDay(date)
        datetimein = datetime.datetime.combine(date, datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(date, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        return datetimein, datetimeout

@method_decorator(login_required, name='dispatch')
class ActLast3View(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        dateout = utils.getTime().date()
        datein = dateout
        for k in range(2): datein = utils.getPrevDay(datein)
        datetimein = datetime.datetime.combine(datein, datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(dateout, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        return datetimein, datetimeout

@method_decorator(login_required, name='dispatch')
class ActLast7View(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        dateout = utils.getTime().date()
        datein = dateout
        while datein.strftime("%A") != "Monday": datein = utils.getPrevDay(datein)
        datetimein = datetime.datetime.combine(datein, datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(dateout, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        return datetimein, datetimeout

@method_decorator(login_required, name='dispatch')
class ActFromPathView(ActView):

    def _getPeriod(self, **kwargs) -> tuple:
        datein = datetime.datetime.strptime(kwargs['datein'], "%d.%m.%Y")
        dateout = datetime.datetime.strptime(kwargs['dateout'], "%d.%m.%Y")
        datetimein = datetime.datetime.combine(datein, datetime.datetime.strptime("00:00:00", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        datetimeout = datetime.datetime.combine(dateout, datetime.datetime.strptime("23:59:59", "%H:%M:%S").time(), tzinfo=pytz.timezone(settings.TIME_ZONE))
        # datetimein = utils.getTime(datetimein)
        # datetimeout = utils.getTime(datetimeout)
        # print(datetimein, datetimeout)
        return datetimein, datetimeout

@method_decorator(login_required, name='dispatch')
class ActUserFromPathView(ActFromPathView):
    template_name = 'activityUser.html'

    def get(self, request, *args, **kwargs):
        if request.user.role in ("Manager", "Admin"):
            user = models.User.objects.get(username=kwargs['username'])
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

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(show_edit=True)
        return context

#region Come Left

def user_come(request, datein, dateout, username):
    pass

#endregion

#endregion
#endregion

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
                    user.groups.all().delete()
                    group = Group.objects.get(name=user.role)
                    user.groups.add(group)
                    user.save(force_update=True)
                else:
                    user.save(force_update=True)
                    login(request, user)
                messages.success(request, ("Modificarile au fost efectuate!"))
        else: messages.success(request, ("Nu exista nici o modificare!"))
    return render(request, 'detalii.html', {"userdata": user})
