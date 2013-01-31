from jsonclient import Mapping, TextField, DateField, ListField, DictField, IntegerField, BooleanField
from larryslist.models import ClientTokenProc
from larryslist.models.config import GenreModel, MediumModel

__author__ = 'Martin'


class SourceModel(Mapping):
    """
        { "type": "Book", "url": "asdfa", "-name": "asdf", "publisher": "ASDF", "title": "asdf", "author": "zsdfa", "date": "01.01.1979", "year": "1234" },
        { "type": "magazine", "url": "as4r56dfa", "name": "as235df", "publisher": "AS2345DF", "title": "a243sdf", "author": "zsdf2435a", "date": "01.01.1979", "year": "1234w43" }
    """
    type = TextField()
    url = TextField()
    name = TextField()
    title = TextField()
    author = TextField()
    date = DateField()
    year = TextField()
    publisher = TextField()

class ArtistModel(Mapping):
    name = TextField()

class CollectionRegionModel(Mapping):
    name = TextField()

class PublisherModel(Mapping):
    title = TextField()
    year = TextField()
    publisher = TextField()

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
    Publisher = ListField(DictField(PublisherModel))

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

class LinkedCollectorModel(Mapping):
    id = IntegerField()
    firstName = TextField()
    lastName = TextField()
    def getName(self):
        return u'{firstName} {lastName}'.format(firstName = self.firstName, lastName = self.lastName)


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
    Source = DictField(SourceModel)
    LinkedCollector = DictField(LinkedCollectorModel)
    def getName(self):
        return u'{firstName} {lastName}'.format(firstName = self.firstName, lastName = self.lastName)

CreateCollectorProc = ClientTokenProc("/admin/collector/create", root_key = 'Collector', result_cls=CollectorModel)
GetCollectorDetailsProc = ClientTokenProc("/admin/collector", root_key = 'Collector', result_cls=CollectorModel)

EditCollectorBaseProc = ClientTokenProc("/admin/collector/basicedit", root_key = 'Collector', result_cls=CollectorModel)
EditCollectorContactsProc = ClientTokenProc("/admin/collector/contactedit", root_key = 'Collector', result_cls=CollectorModel)
EditCollectorBusinessProc = ClientTokenProc("/admin/collector/businessedit", root_key = 'Collector', result_cls=CollectorModel)

SetSourcesProc = ClientTokenProc("/admin/collector/sourceedit", root_key = 'Collector', result_cls=CollectorModel)

CreateCollectionProc = ClientTokenProc("/admin/collection/create", root_key = 'Collection', result_cls=CollectionModel)
EditCollectionBaseProc = ClientTokenProc("/admin/collection/basicedit", root_key = 'Collection', result_cls=CollectionModel)
EditCollectionArtistsProc = ClientTokenProc("/admin/collection/artistedit", root_key = 'Collection', result_cls=CollectionModel)
EditCollectionPublicationsProc = ClientTokenProc("/admin/collection/communicationedit", root_key = 'Collection', result_cls=CollectionModel)

SaveCollectorDocumentsProc = ClientTokenProc("/admin/collector/document", root_key = 'Collection', result_cls=CollectionModel)
SaveCollectionDocumentsProc = ClientTokenProc("/admin/collection/document", root_key = 'Collection', result_cls=CollectionModel)