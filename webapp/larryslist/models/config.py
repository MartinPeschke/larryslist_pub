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

class GenderModel(Mapping):
    key = TextField()
    label = TextField()
    def getKey(self, request):return self.key
    def getLabel(self, request):return self.label

GENDER_CHOICES = [GenderModel(key = 'm', label = 'male'), GenderModel(key = 'f', label = 'female')]



class ConfigModel(Mapping):
    Nationality = ListField(DictField(NationalityModel))
    Title = ListField(DictField(TitleModel))
    Industry = ListField(DictField(IndustryModel))
    Position = ListField(DictField(PositionModel))
    Interest = ListField(DictField(InterestModel))
    Gender = GENDER_CHOICES