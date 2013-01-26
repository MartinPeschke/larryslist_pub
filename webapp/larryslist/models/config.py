from jsonclient import Mapping, TextField, DictField, ListField

__author__ = 'Martin'

class NamedConfigModel(Mapping):
    name = TextField()
    def getKey(self, request):return self.name
    def getLabel(self, request):return self.name

class NationalityModel(NamedConfigModel): pass
class TitleModel(NamedConfigModel): pass
class IndustryModel(NamedConfigModel): pass
class PositionModel(NamedConfigModel): pass
class InterestModel(NamedConfigModel): pass
class SocNetModel(NamedConfigModel): pass
class MediumModel(NamedConfigModel): pass
class GenreModel(NamedConfigModel): pass
class PublisherModel(NamedConfigModel): pass
class SourceTypeModel(NamedConfigModel): pass

class GenderModel(Mapping):
    key = TextField()
    label = TextField()
    def getKey(self, request):return self.key
    def getLabel(self, request):return self.label

GENDER_CHOICES = [GenderModel(key = 'm', label = 'male'), GenderModel(key = 'f', label = 'female')]
SOCIAL_NETWORKS = [SocNetModel(name = 'Facebook'), SocNetModel(name = 'Linkedin'), SocNetModel(name = 'Twitter'), SocNetModel(name = 'Other')]
PUBLISHER_CHOICES = [PublisherModel(name= 'Pub %d'%i) for i in range(20)]

SOURCE_TYPES = [SourceTypeModel(name='blog'), SourceTypeModel(name = 'book')]

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
    Publisher = PUBLISHER_CHOICES
    SourceType = SOURCE_TYPES