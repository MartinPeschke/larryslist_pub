from operator import methodcaller
from jsonclient import Mapping, IntegerField, TextField, ListField, DictField
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