from jsonclient import Mapping, TextField, DateField, ListField, DictField, IntegerField
from larryslist.models import ClientTokenProc

__author__ = 'Martin'

class CollectionModel(Mapping):
    id = IntegerField()



class LocationModel(Mapping):
    name = TextField()
    token = TextField()

class AddressModel(Mapping):
    line1 = TextField()
    postCode = TextField()
    Country = LocationModel()
    Region = LocationModel()
    City = LocationModel()

class UniversityModel(Mapping):
    name = TextField()
    city = TextField()

class CollectorModel(Mapping):
    id = IntegerField()
    firstName = TextField()
    lastName = TextField()
    origName = TextField()
    dob = DateField()
    Nationality = TextField()
    Title = TextField()
    Gender = TextField()
    Address = ListField(DictField(AddressModel))
    University = ListField(DictField(UniversityModel))
    Collection = DictField(CollectionModel)

CreateCollectorProc = ClientTokenProc("/admin/collector/create", root_key = 'Collector', result_cls=CollectorModel)
GetCollectorDetailsProc = ClientTokenProc("/admin/collector", root_key = 'Collector', result_cls=CollectorModel)

EditCollectorBaseProc = ClientTokenProc("/admin/collector/basicedit", root_key = 'Collector', result_cls=CollectorModel)
EditCollectorContactsProc = ClientTokenProc("/admin/collector/contactedit", root_key = 'Collector', result_cls=CollectorModel)
EditCollectorBusinessProc = ClientTokenProc("/admin/collector/businessedit", root_key = 'Collector', result_cls=CollectorModel)


CreateCollectionProc = ClientTokenProc("/admin/collection/create", root_key = 'Collection', result_cls=CollectionModel)
EditCollectionBaseProc = ClientTokenProc("/admin/collection/basicedit", root_key = 'Collection', result_cls=CollectionModel)
