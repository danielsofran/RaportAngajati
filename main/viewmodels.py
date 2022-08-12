import datetime

from . import models
from . import utils

class RowDataActivity:
    def __init__(self, user: models.User, data: datetime.datetime, mintold, filtersin=None, filtersout=None, filterscmd=None):
        if filtersin is None: filtersin = {}
        if filtersout is None: filtersout = {}
        if filterscmd is None: filterscmd = {}
        self.__mins = mintold
        self.__now = utils.getTime()
        self.user = user
        self.datetime = data
        self.absent = False
        self.__nu_respecta_filtru = False
        self.__activities = 4
        self.intrari = models.Intrare.objects.filter(user=user, datetime__date=data.date(), **filtersin)
        self.first_intrare = self.intrari.order_by("-datetime").first()
        if self.intrari.count() == 0: self.__activities -= 1
        self.iesiri = models.Iesire.objects.filter(user=user, datetime__date=data.date(), **filtersout)
        self.first_iesire = self.iesiri.order_by("-datetime").first()
        if self.iesiri.count() == 0: self.__activities -= 1
        dif = self.intrari.count() - self.iesiri.count()
        if dif == 1: self.first_iesire = models.Iesire.objects.none()
        elif dif == -1: self.first_intrare = models.Intrare.objects.none()

        self.comenzi = models.Comanda.objects.filter(user=user, datetime__date=data.date(), **filterscmd)
        self.nrcomenzi = self.comenzi.__len__()
        if self.nrcomenzi == 0: self.__activities -= 1
        self.lucrari = models.Lucru.objects.filter(user=user, datetime__date=data.date())
        self.nrlucrari = self.lucrari.__len__()
        if self.nrlucrari == 0: self.__activities -= 1
        if self.__activities == 0: self.absent = True
        self.numecomenzi = ""
        for comanda in self.comenzi:
            self.numecomenzi += comanda.denumire+"<br>"

    def hasCmd(self, cmd: str) -> bool:
        rez = self.comenzi.filter(numar_comanda__startswith=cmd).count()
        return rez > 0

    @property
    def color(self):
        if self.__now.date() != self.datetime.date():
            if self.__activities == 0: return 'class=\'table-warning\''
            elif self.__activities == 4: return 'class=\'table-success\''
        elif self.__activities == 4:
            return 'class=\'table-success\''
        return ""


    def __lt__(self, other):
        return self.user.nume < other.user.nume or \
               self.user.nume == other.user.nume and self.datetime < other.datetime


class Carousel:
    maxid = 1

    class Item:
        def __init__(self, src, html="", alt="", index=0):
            self.index = index
            self.src = src
            self.html = html
            self.alt = alt

    def __init__(self):
        self.ownid = Carousel.maxid
        Carousel.maxid += 1
        self.items = []

    def addItem(self, src, html="", alt=""):
        self.items.append(self.Item(src, html, alt, len(self.items)))

