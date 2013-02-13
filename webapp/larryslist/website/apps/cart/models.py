from operator import methodcaller
from jsonclient import Mapping, IntegerField, TextField, ListField, DictField
from larryslist.models import ClientTokenProc
from larryslist.website.apps.auth.models import LoggingInProc
import simplejson



class LocationModel(Mapping):
    name = TextField()
    token = TextField()

class AddressModel(Mapping):
    Country = LocationModel()
    Region = LocationModel()
    City = LocationModel()

class CollectorModel(Mapping):
    id = IntegerField()
    status = TextField()
    initials = TextField()
    picture = TextField()
    rank = TextField()
    subscribers = TextField()
    completion = TextField()
    Address = ListField(DictField(AddressModel))
    def getName(self):
        return self.initials

    def getAddress(self):
        if not len(self.Address): return ''
        addr = self.Address[0]
        if not addr.Region or not addr.Country: return ''
        return u"{region}, {country}".format(region = addr.Region.name, country = addr.Country.name)



class WebsiteCart(CollectorModel):
    Collectors = []
    def setContent(self, json):
        self.Collectors = map(CollectorModel.wrap, json.get('Collectors', []))
    def getContent(self, stringify = False):
        try:
            cart = map(methodcaller("unwrap", sparse = True), self.Collectors)
        except AttributeError, e:
            cart = []
        return simplejson.dumps({'Collectors':cart})

    def getItems(self):
        return self.Collectors

    def canSpend(self, user):
        return user.getCredits() >= len(self.getItems()) > 0
    def empty(self):
        self.Collectors = []

PurchaseCreditProc = ClientTokenProc("/web/credit/buy")
SpendCreditProc = LoggingInProc("/web/credit/spend")