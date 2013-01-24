from jsonclient import Mapping, TextField, DateField, ListField, DictField
from larryslist.models import ClientTokenProc

__author__ = 'Martin'


class AddressModel(Mapping):
    line1 = TextField()
    postCode = TextField()
    city = TextField()

class UniversityModel(Mapping):
    name = TextField()
    city = TextField()

class CollectorModel(Mapping):
    firstName = TextField()
    lastName = TextField()
    origName = TextField()
    dob = DateField()
    Nationality = TextField()
    Title = TextField()
    Gender = TextField()
    Address = ListField(DictField(AddressModel))
    University = ListField(DictField(UniversityModel))

CreateCollectorProc = ClientTokenProc("/admin/collector/create", root_key = 'Collector', result_cls=CollectorModel)
