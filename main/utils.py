import datetime
from django import utils
import pytz
from django.utils.timezone import activate, localtime

import main.models
from siteReport import settings

def getTime(info: main.models.Info = None):
    if info is None: now = utils.timezone.now()
    else: now = info.datetime
    settings_time_zone = pytz.timezone(settings.TIME_ZONE)
    now = now.astimezone(settings_time_zone)
    return now

def secureStr(text) -> str:
    return str(text).replace("script", "")
