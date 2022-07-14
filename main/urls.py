from django.contrib.auth.decorators import login_required
from django.urls import path

from . import views

urlpatterns = [
    path("", views.login_user, name="mylogin"),
    path("logout", views.logout_user, name="mylogout"),
    path("home", login_required(views.HomeView.as_view()), name="home"),
    path("home/come", login_required(views.come), name="come"),
    path("home/left", login_required(views.left), name="left"),
    path("detalii", login_required(views.HomeView.as_view()), name="detalii"),
]