from jsonclient import Mapping, TextField, DateField, ListField, DictField, IntegerField, BooleanField
from larryslist.models import ClientTokenProc
from larryslist.models.config import GenreModel, MediumModel

__author__ = 'Martin'


class ArtistModel(Mapping):
    name = TextField()

class CollectionRegionModel(Mapping):
    name = TextField()



class CollectionModel(Mapping):
    id = IntegerField()
    name = TextField()
    totalWorks = IntegerField()
    totalWorksAprx = BooleanField()
    totalArtists = IntegerField()
    totalArtistsAprx = BooleanField()
    foundation = TextField()
    started = TextField()
    Genre = ListField(DictField(GenreModel))
    Medium = ListField(DictField(MediumModel))
    Artist = ListField(DictField(ArtistModel))
    Region = ListField(DictField(CollectionRegionModel))


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
EditCollectionArtistsProc = ClientTokenProc("/admin/collection/artistedit", root_key = 'Collection', result_cls=CollectionModel)
EditCollectionPublicationsProc = ClientTokenProc("/admin/collection/artistedit", root_key = 'Collection', result_cls=CollectionModel)
