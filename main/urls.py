from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path("", views.login_user, name="mylogin"),
    path("logout", views.logout_user, name="mylogout"),

    path("home", login_required(views.HomeView.as_view()), name="home"),
    path("home/come", login_required(views.come), name="come"),
    path("home/left", login_required(views.left), name="left"),
    path("home/cancel_come", login_required(views.cancel_come), name="cancel_come"),
    path("home/cancel_left", login_required(views.cancel_left), name="cancel_left"),
    path("home/come_recalc", login_required(views.recalc_come), name="come_recalc"),
    path("home/left_recalc", login_required(views.recalc_left), name="left_recalc"),

    path("comanda/finish", login_required(views.comandaFinish), name="comanda_finish"),
    path("detalii", login_required(views.HomeView.as_view()), name="detalii"),
]