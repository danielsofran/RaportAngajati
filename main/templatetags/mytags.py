import datetime

from django import template
from main import utils, models
from siteReport import settings
import pytz
register = template.Library()

@register.filter(name='has_group')
def has_group(user, group_name):
    return user.groups.filter(name=group_name).exists()

@register.filter(name='role_at_least')
def role_at_least(user, name):
    priorit = {
        "Angajat": 1,
        "Viewer": 2,
        "Manager": 3,
        "Admin": 4,
    }
    if not user.is_authenticated:
        return False
    if name in priorit.keys():
        return priorit[user.role] >= priorit[name]
    return False

@register.filter(name='is_recent')
def is_recent(user, tip):
    if not role_at_least(user, "Angajat"): return False
    model = None
    if tip == 'In': model = models.Intrare
    elif tip == 'Out': model = models.Iesire

    SEC_RECALC_AFTER = 60
    NR_RECALC_POZ = 3
    try:
        setare = models.OwnSettings.objects.all()[0]
        SEC_RECALC_AFTER = setare.secafterrecalc
        NR_RECALC_POZ = setare.nrrecalcpoz
    except:
        print("Nu exista setari")

    if model is not None:
        now = utils.getTime()
        info = model.objects.filter(user=user, datetime__day=now.day).order_by("-datetime").first()
        if info is None: return False
        dtime = now - info.datetime
        if dtime.seconds <= SEC_RECALC_AFTER:
            return True
    return False

@register.filter(name='ftime')
def ftime(datetimegiven: datetime.datetime, tip: str) -> str:
    if datetimegiven is None or str(datetimegiven).__len__() == 0: return "-"
    datetimegiven = utils.getTime(datetimegiven)
    if tip == "time": return datetimegiven.strftime("%H:%M")
    if tip == "date": return datetimegiven.strftime("%d.%m.%Y")
    if tip == "datetime": return datetimegiven.strftime("%d.%m.%Y-%H:%M")
    if tip == "date timenow":
        time = utils.getTime().time()
        datetimegiven = datetime.datetime.combine(datetimegiven.date(), time, tzinfo=pytz.timezone(settings.TIME_ZONE))
        return datetimegiven.strftime("%d.%m.%Y-%H:%M")
    return "-"

@register.filter(name='name_of_day')
def name_of_day(datetime: datetime.datetime) -> str:
    asocs = {
        "Monday": "Luni",
        "Tuesday": "Marti",
        "Wednesday": "Miercuri",
        "Thursday": "Joi",
        "Friday": "Vineri",
        "Saturday": "Sambata",
        "Sunday": "Duminica",
    }
    return asocs[datetime.strftime("%A")]

@register.filter(name='strloc')
def strloc(info: models.Info) -> str:
    return utils.locStr(info)

@register.filter(name='strobs')
def strobs(obs: str) -> str:
    return obs.replace("; ", "\n")
