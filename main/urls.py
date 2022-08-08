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

    path("home/comanda/finish", login_required(views.comandaFinish), name="comanda_finish"),
    path("home/comanda/cancel", login_required(views.comandaCancel), name="comanda_cancel"),
    path("home/comanda/edit", login_required(views.comandaEdit), name="comanda_edit"),

    path("home/lucru/finish", login_required(views.lucruFinish), name="lucru_finish"),
    path("home/lucru/cancel", login_required(views.lucruCancel), name="lucru_cancel"),
    path("home/lucru/edit", login_required(views.lucruEdit), name="lucru_edit"),

    path("activity/today", login_required(views.ActTodayView.as_view()), name="actToday"),
    path("activity/yesterday", login_required(views.ActYesterdayView.as_view()), name="actYesterday"),
    path("activity/2daysago", login_required(views.Act2DaysAgoView.as_view()), name="act2daysAgo"),
    path("activity/last3", login_required(views.ActLast3View.as_view()), name="actLast3"),
    path("activity/last7", login_required(views.ActLast7View.as_view()), name="actLast7"),

    path("activity/<str:datein>,<str:dateout>", login_required(views.ActFromPathView.as_view()), name="actFromPath"),
    path("activity/<str:datein>,<str:dateout>/<str:username>", login_required(views.ActUserFromPathView.as_view()), name="actUserFromPath"),
    path("activity/getperiod", login_required(views.getperiod), name="actGetPeriod"),
    path("activity/getperioduser", login_required(views.getperioduser), name="actGetPeriodUser"),
    path("activity/delete", login_required(views.getperioddelete), name="actDelete"),

    path("activity/intrare", login_required(views.IntrareActivity.as_view()), name="intrare"),
    path("activity/intrare/<str:date>/<str:username>", login_required(views.IntrareActivity.as_view()), name="intrareUser"),
    path("activity/iesire", login_required(views.IesireActivity.as_view()), name="iesire"),
    path("activity/iesire/<str:date>/<str:username>", login_required(views.IesireActivity.as_view()), name="iesireUser"),
    path("activity/comenzi", login_required(views.ComandaActivity.as_view()), name="comenzi"),
    path("activity/comenzi/<str:date>/<str:username>", login_required(views.ComandaActivity.as_view()), name="comenziUser"),
    path("activity/lucrari", login_required(views.LucruActivity.as_view()), name="lucrari"),
    path("activity/lucrari/<str:date>/<str:username>", login_required(views.LucruActivity.as_view()), name="lucrariUser"),

    path("cont/detalii", login_required(views.detalii), name="detalii"),
    path("cont/users", login_required(views.Utilizatori.as_view()), name="utilizatori"),
    path("cont/detalii/<str:username>", login_required(views.detalii), name="detaliiuser"),
    path("cont/add", login_required(views.adduser), name="adduser"),
    path("cont/<str:username>/delete", login_required(views.deleteuser), name="deleteuser"),

    path("setari", login_required(views.Setari.as_view()), name="setari"),
    path("setari/delete_harta/<int:hid>", login_required(views.stergeharta), name="stergeharta"),
    path("setari/delete_forma/<int:fid>", login_required(views.stergeforma), name="stergeforma"),

    path("about", login_required(views.about), name="about"),
]