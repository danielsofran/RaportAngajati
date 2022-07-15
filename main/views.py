from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from . import models
from . import utils

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

        messages.success(request, ("Utilizator inexistent!"))
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
        try:
            data = models.Intrare.objects.get(datetime__day=now.day)
            messages.success(request, ("Momentul intrarii a fost deja inregistrat!\nVa rugam sa il stergeti daca a fost adaugat din greseala!"))
            return redirect('home')
        except:
            models.Intrare.objects.create(user=request.user, latitude=request.GET['lat'], longitude=request.GET['long'], datetime=now, nrcalcloc=1, text=request.GET['obs'])
            messages.success(request, ("Succes!"))
            messages.success(request, ("Daca considerati ca locatia nu este precisa(erori de peste 10-20m), puteti sa folositi butonul relocare de maxim 3 ori.\nTimpul limita pentru o relocare este de un minut dupa ultima relocare."))
    else: raise ValueError("POST in come")
    return redirect('home')
6
def cancel_come(request):
    now = utils.getTime()
    try: data = models.Intrare.objects.get(datetime__day=now.day)
    except:
        messages.success(request, ("Momentul intrarii nu a fost inregistrat!"))
        return redirect('home')
    data.delete()
    messages.success(request, ("Momentul intrarii a fost sters!"))
    return redirect('home')

def recalc_come(request):
    try:
        now = utils.getTime()
        data = models.Intrare.objects.get(datetime__day=now.day)
        if (now-utils.getTime(data)).seconds > 60:
            raise ValueError("Timpul pentru relocare a expirat!")
        nr = data.nrcalcloc
        if nr <= 3:
            data.nrcalcloc = data.nrcalcloc + 1
            data.latitude = request.GET['lat']
            data.longitude = request.GET['long']
            data.save(update_fields=['latitude', 'longitude', 'nrcalcloc'])
            messages.success(request, (f"Locatie actualizata! Mai aveti {4 - data.nrcalcloc} relocari."))
        else: messages.success(request, (f"Nu mai aveti relocari disponibile."))
    except: messages.success(request, ("Timpul pentru relocare a expirat!"))
    return redirect('home')

def left(request):
    now = utils.getTime()
    if models.Intrare.objects.filter(datetime__day=now.day).__len__() == 0:
        messages.success(request, (f"Nu puteti parasi inainte sa intrati!"))
        return redirect('home')
    try:
        data = models.Iesire.objects.get(datetime__day=now.day)
        messages.success(request, ("Momentul iesirii a fost deja inregistrat!\nVa rugam sa il stergeti daca a fost adaugat din greseala!"))
        return redirect('home')
    except:
        models.Iesire.objects.create(user=request.user, latitude=request.GET['lat'], longitude=request.GET['long'], datetime=now, nrcalcloc=1, text=request.GET['obs'])
        messages.success(request, ("Succes!"))
        messages.success(request, ("Daca considerati ca locatia nu este precisa(erori de peste 10-20m), puteti sa folositi butonul relocare de maxim 3 ori.\nTimpul limita pentru o relocare este de un minut dupa ultima relocare."))
    return redirect('home')

def cancel_left(request):
    now = utils.getTime()
    try:
        models.Intrare.objects.get(datetime__day=now.day)
        messages.success(request, (f"Nu puteti parasi inainte sa intrati!"))
        return redirect('home')
    except: pass
    try: data = models.Iesire.objects.get(datetime__day=now.day)
    except:
        messages.success(request, ("Momentul iesirii nu a fost inregistrat!"))
        return redirect('home')
    data.delete()
    messages.success(request, ("Momentul iesirii a fost sters!"))
    return redirect('home')

def recalc_left(request):
    now = utils.getTime()
    try:
        models.Intrare.objects.get(datetime__day=now.day)
        messages.success(request, (f"Nu puteti parasi inainte sa intrati!"))
        return redirect('home')
    except: pass
    try:
        data = models.Iesire.objects.get(datetime__day=now.day)
        if (now-utils.getTime(data)).seconds > 60:
            raise ValueError("Timpul pentru relocare a expirat!")
        nr = data.nrcalcloc
        if nr <= 3:
            data.nrcalcloc = data.nrcalcloc + 1
            data.latitude = request.GET['lat']
            data.longitude = request.GET['long']
            data.save(update_fields=['latitude', 'longitude', 'nrcalcloc'])
            messages.success(request, (f"Locatie actualizata! Mai aveti {4 - data.nrcalcloc} relocari."))
        else: messages.success(request, (f"Nu mai aveti relocari disponibile."))
    except: messages.success(request, ("Nu exista o locatie initiala ce poate fi actualizata"))
    return redirect('home')

#endregion

def comandaFinish(request):
    if request.method == "GET":
        now = utils.getTime()
        try:
            models.Comanda.objects.get(numar_comanda=request.GET['nrcom'])
            messages.success(request, ("Aceasta comanda exista deja!"))
            return redirect('home')
        except:
            models.Comanda.objects.create(user=request.user, latitude=request.GET['lat'],
                                          longitude=request.GET['long'], datetime=now,
                                          nrcalcloc=1, text=request.GET['obs'], numar_comanda=request.GET['nrcom'], denumire=request.GET['den'])
            messages.success(request, ("Succes! Finalizarea a fost inregistrata!"))
    else:
        raise ValueError("POST in comand finish")
    return redirect('home')

@method_decorator(login_required, name='dispatch')
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context2 = {
            'oraIn': "12:34",
            'oraOut': "12:23",
            'locIn': "47.1797339,24.1702929",
            'locOut': "47.1796205,24.1712729",
            'locStrIn': "in firma",
            'locStrOut': "aproape de firma",
            'observatie': 'am facut 2 piese',
        }
        context2 = {
            'oraIn': "-",
            'oraOut': "-",
            'locIn': "-",
            'locOut': "-",
            'locStrIn': "-",
            'locStrOut': "-",
            'observatie': "-",
        }
        now = utils.getTime()
        user = self.request.user

        # In
        try:
            gasit = models.Intrare.objects.get(datetime__day=now.day)
            context2['oraIn'] = utils.getTime(gasit).strftime("%H:%M")
            context2['locIn'] = f"{gasit.latitude},{gasit.longitude}"
            context2['obsIn'] = gasit.text
        except:
            context2['oraIn'] = "-"
            context2['locIn'] = "-"
            context2['obsIn'] = ""

        # Out
        try:
            gasit = models.Iesire.objects.get(datetime__day=now.day)
            context2['oraOut'] = utils.getTime(gasit).strftime("%H:%M")
            context2['locOut'] = f"{gasit.latitude},{gasit.longitude}"
            context2['obsOut'] = gasit.text
        except:
            context2['oraOut'] = "-"
            context2['locOut'] = "-"
            context2['obsOut'] = ""

        #Comenzi
        try:
            comenzi = models.Comanda.objects.filter(user=user)
            context2['comenzi'] = comenzi
        except:
            context2['comenzi'] = []
        context.update(context2)
        return context
#endregion