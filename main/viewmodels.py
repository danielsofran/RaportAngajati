import datetime

from . import models

class RowDataActiviy:
    def __init__(self, user: models.User, data: datetime.datetime):
        self.user = user
        self.datetime = data
        self.absent = False
        activities = 3
        try: self.intrare = models.Intrare.objects.get(user=user, datetime__day=data.day, datetime__month=data.month, datetime__year=data.year)
        except: activities-=1
        try: self.iesire = models.Iesire.objects.get(user=user, datetime__day=data.day, datetime__month=data.month, datetime__year=data.year)
        except: activities-=1
        self.comenzi = models.Comanda.objects.filter(user=user, datetime__day=data.day, datetime__month=data.month, datetime__year=data.year)
        self.nrcomenzi = self.comenzi.__len__()
        if self.nrcomenzi == 0: activities-=1
        if activities == 0:
            self.absent = True
        self.numecomenzi = ""
        for comanda in self.comenzi:
            self.numecomenzi += comanda.denumire+"<br>"

    def __lt__(self, other):
        return self.user.nume < other.user.nume or \
               self.user.nume == other.user.nume and self.datetime < other.datetime
