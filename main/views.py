import datetime

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import user_passes_test, login_required
from django.utils.decorators import method_decorator
from django.views.generic import View, TemplateView, ListView, DetailView, CreateView, UpdateView, DeleteView

from . import models

# Create your views here.

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

def come(request):
    if request.method == 'GET':
        current = datetime.datetime.now()
        try:
            models.Intrare.objects.get(datetime__day=current.day)
            messages.success(request, ("Momentul intrarii a fost inregistrat!\nVa rugam sa il stergeti daca a fost adaugat din greseala!"))
            return redirect('home')
        except:
            models.Intrare.objects.create(user=request.user, latitude=request.GET['lat'], lognitude=request.GET['long'], datetime=current, )
    else:
        raise ValueError("POST in come")
    return redirect('home')

def left(request):
    current = datetime.datetime.now()
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
        # context2 = {
        #     'oraIn': "-",
        #     'oraOut': "-",
        #     'locIn': "-",
        #     'locOut': "-",
        #     'locStrIn': "-",
        #     'locStrOut': "-",
        #     'observatie': "-",
        # }
        current = datetime.datetime.now() # atentie la timezone
        user = self.request.user
        try:
            gasit = models.Intrare.objects.get(datetime__day=current.day)
            context2['oraIn'] = f"{gasit.time.hour}:{gasit.time.minute}"
        except: pass
        try:
            gasit = models.Iesire.objects.get(datetime__day=current.day)
            context2['oraOut'] = f"{gasit.time.hour}:{gasit.time.minute}"
        except: pass
        #Info
        context.update(context2)
        return context
