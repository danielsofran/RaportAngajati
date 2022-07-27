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
        self.intrare = None
        self.iesire = None
        self.user = user
        self.datetime = data
        self.absent = False
        self.__nu_respecta_filtru = False
        activities = 3
        try: self.intrare = models.Intrare.objects.get(user=user, datetime__date=data.date(), **filtersin)
        except: activities -= 1
        try: self.iesire = models.Iesire.objects.get(user=user, datetime__date=data.date(), **filtersout)
        except: activities -= 1
        self.comenzi = models.Comanda.objects.filter(user=user, datetime__date=data.date(), **filterscmd)
        self.nrcomenzi = self.comenzi.__len__()
        if self.nrcomenzi == 0: activities -= 1
        if activities == 0: self.absent = True
        self.numecomenzi = ""
        for comanda in self.comenzi:
            self.numecomenzi += comanda.denumire+"<br>"

    class structDate:
        datetime = datetime.datetime.strptime("01.01.2001 00:00:00", "%d.%m.%Y %H:%M:%S")
        text = ""

    @property
    def intrare_notnone(self):
        if self.intrare is not None: return self.intrare
        return self.structDate

    @property
    def iesire_notnone(self):
        if self.iesire is not None: return self.iesire
        return self.structDate

    def hasCmd(self, cmd: str) -> bool:
        rez = self.comenzi.filter(numar_comanda__startswith=cmd).count()
        return rez > 0

    @property
    def __isLocationWarning(self) -> bool:
        infos = [self.intrare, self.iesire]
        for info in infos:
            if info is not None and utils.locStr(info) != "In firma":
                return True
        return False

    @property
    def notAllDataCompleted(self) -> bool:
        return self.intrare is None or self.iesire is None

    @property
    def noneDataCompleted(self) -> bool:
        return self.intrare is None and self.iesire is None

    @property
    def __hasWorked8Hours(self) -> bool:
        if not self.notAllDataCompleted:
            delta = self.iesire.datetime - self.intrare.datetime
            delta2 = datetime.timedelta(hours=8)
            delta2 -= datetime.timedelta(minutes=self.__mins)
            return delta >= delta2
        return True

    @property
    def color(self):
        if self.__isLocationWarning: return 'class=\'table-warning\''
        if not self.__hasWorked8Hours: return 'class=\'table-info\''
        if self.__now.date() != self.datetime.date():
            if self.notAllDataCompleted: return 'class=\'table-secondary\''
            return 'class=\'table-success\''
        elif not self.notAllDataCompleted:
            return 'class=\'table-success\''
        return ""


    def __lt__(self, other):
        return self.user.nume < other.user.nume or \
               self.user.nume == other.user.nume and self.datetime < other.datetime



