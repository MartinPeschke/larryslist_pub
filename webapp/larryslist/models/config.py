from jsonclient import Mapping, TextField, DictField, ListField

__author__ = 'Martin'

class NullConfigModel(Mapping):
    name = TextField()
    def getKey(self, request):return ''
    def getLabel(self, request):return '---'


class NamedConfigModel(Mapping):
    name = TextField()
    def getKey(self, request):return self.name
    def getLabel(self, request):return self.name

class NationalityModel(NamedConfigModel): pass
class TitleModel(NamedConfigModel): pass
class IndustryModel(NamedConfigModel): pass
class PositionModel(NamedConfigModel): pass
class CollectionPositionModel(NamedConfigModel): pass
class CooperationTypeModel(NamedConfigModel): pass
class TopMuseumModel(NamedConfigModel): pass
class InterestModel(NamedConfigModel): pass
class SocNetModel(NamedConfigModel): pass
class MediumModel(NamedConfigModel): pass
class GenreModel(NamedConfigModel): pass
class PublisherModel(NamedConfigModel): pass
class SourceTypeModel(NamedConfigModel): pass
class DocumentTypeModel(NamedConfigModel): pass
class GenderModel(Mapping):
    key = TextField()
    label = TextField()
    def getKey(self, request):return self.key
    def getLabel(self, request):return self.label

GENDER_CHOICES = [GenderModel(key = 'm', label = 'male'), GenderModel(key = 'f', label = 'female')]
SOCIAL_NETWORKS = [SocNetModel(name = 'Facebook'), SocNetModel(name = 'Linkedin'), SocNetModel(name = 'Twitter'), SocNetModel(name = 'Other')]
DOCUMENT_TYPES = [DocumentTypeModel(name = 'IMAGE'), DocumentTypeModel(name = 'OTHER')]

CPM = CollectionPositionModel
COLLECTION_POSITIONS = [CPM(name = "Director"), CPM(name = "Curator"), CPM(name = "Head of Collection")]
CTM = CooperationTypeModel
COOPERATION_TYPES = [CTM(name = "Exhibition of own collection"), CTM(name = "Sponsoring"), CTM(name = "Funding of Award"), CTM(name = "Support of educational program")]

TOP_MUSEUMS = [TopMuseumModel(name = "Museum-{}".format(i)) for i in range(100)]


class ConfigModel(Mapping):
    Nationality = ListField(DictField(NationalityModel))
    Title = ListField(DictField(TitleModel))
    Industry = ListField(DictField(IndustryModel))
    Position = ListField(DictField(PositionModel))
    Medium = ListField(DictField(MediumModel))
    Genre = ListField(DictField(GenreModel))
    Interest = ListField(DictField(InterestModel))
    Network = SOCIAL_NETWORKS
    Gender = GENDER_CHOICES
    Publisher = ListField(DictField(PublisherModel))
    SourceType = ListField(DictField(SourceTypeModel))
    DocumentType = DOCUMENT_TYPES
    CollectionPosition = COLLECTION_POSITIONS
    CooperationType = COOPERATION_TYPES
    TopMuseum = TOP_MUSEUMS