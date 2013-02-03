from jsonclient import Mapping, TextField, DictField, ListField

__author__ = 'Martin'

class NullConfigModel(Mapping):
    name = TextField()
    def getKey(self, request):return ''
    def getLabel(self, request):return '---'


class NamedModel(Mapping):
    name = TextField()
    def getKey(self, request):return self.name
    def getLabel(self, request):return self.name

class NationalityModel(NamedModel): pass
class TitleModel(NamedModel): pass
class IndustryModel(NamedModel): pass
class PositionModel(NamedModel): pass
class CollectionPositionModel(NamedModel): pass
class CooperationTypeModel(NamedModel): pass
class TopMuseumModel(NamedModel): pass
class InterestModel(NamedModel): pass
class SocNetModel(NamedModel): pass
class MediumModel(NamedModel): pass
class GenreModel(NamedModel): pass
class PublisherModel(NamedModel): pass
class SourceTypeModel(NamedModel): pass
class DocumentTypeModel(NamedModel): pass
class FeederRoleModel(NamedModel): pass
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
FEEDER_ROLES = [FeederRoleModel(name="REVIEWER"), FeederRoleModel(name="OPERATOR")]

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
    FeederRole = FEEDER_ROLES