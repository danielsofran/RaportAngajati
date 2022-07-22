import datetime

from django import template
from main import utils, models
from siteReport import settings
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
        try: info = model.objects.get(user=user, datetime__day=now.day)
        except: return False
        dtime = now - info.datetime
        if dtime.seconds <= SEC_RECALC_AFTER:
            return True
    return False

@register.filter(name='ftime')
def ftime(datetime: datetime.datetime, tip: str) -> str:
    if datetime is None or str(datetime).__len__() == 0: return "-"
    datetime = utils.getTime(datetime)
    if tip == "time": return datetime.strftime("%H:%M")
    if tip == "date": return datetime.strftime("%d.%m.%Y")
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
