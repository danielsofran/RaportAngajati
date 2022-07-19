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

    if model is not None:
        now = utils.getTime()
        try: info = model.objects.get(user=user, datetime__day=now.day)
        except: return False
        dtime = now - info.datetime
        if dtime.seconds <= settings.SEC_RECALC_AFTER:
            return True
    return False
