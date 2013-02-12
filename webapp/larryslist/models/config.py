from datetime import datetime
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
class RelationshipTypeModel(NamedModel): pass

class InterestModel(NamedModel): pass
class SocNetModel(NamedModel): pass
class MediumModel(NamedModel): pass
class GenreModel(NamedModel): pass
class RankingModel(NamedModel): pass
class PublisherModel(NamedModel): pass
class SourceTypeModel(NamedModel): pass
class DocumentTypeModel(NamedModel): pass
class FeederRoleModel(NamedModel): pass
class ArtFairModel(NamedModel): pass
class GenderModel(Mapping):
    key = TextField()
    label = TextField()
    def getKey(self, request):return self.key
    def getLabel(self, request):return self.label


class TopMuseumModel(NamedModel):
    city = TextField()
    def getLabel(self, request):return u"{0.name} ({0.city})".format(self)
    def getKey(self, request):return u"{0.name} ({0.city})".format(self)
GENDER_CHOICES = [GenderModel(key = 'm', label = 'male'), GenderModel(key = 'f', label = 'female')]
SOCIAL_NETWORKS = [SocNetModel(name = 'Facebook'), SocNetModel(name = 'Linkedin'), SocNetModel(name = 'Twitter'), SocNetModel(name = 'Other')]
DOCUMENT_TYPES = [DocumentTypeModel(name = 'IMAGE'), DocumentTypeModel(name = 'OTHER')]

CPM = CollectionPositionModel
COLLECTION_POSITIONS = [CPM(name = "Director"), CPM(name = "Curator"), CPM(name = "Head of Collection")]
CTM = CooperationTypeModel
COOPERATION_TYPES = [CTM(name = "Exhibition of own collection"), CTM(name = "Sponsoring"), CTM(name = "Funding of Award"), CTM(name = "Support of educational program")]
RM = RankingModel
RANKINGS = [RM(name="ARTnews"), RM(name="Art & Auction"), RM(name="Art Review")]

FEEDER_ROLES = [FeederRoleModel(name="REVIEWER"), FeederRoleModel(name="OPERATOR")]

YEARS = [NamedModel(name = yr) for yr in range(datetime.now().year, datetime.now().year - 50, -1)]

MONTHS = [NamedModel(name = mon) for mon in range(1, 13)]
EXPIRY_YEARS = [NamedModel(name = yr) for yr in range(datetime.now().year, datetime.now().year + 50)]
CARD_TYPES = [NamedModel(name = 'VISA'), NamedModel(name = 'MC'), NamedModel(name = 'AMEX')]







class ConfigModel(Mapping):
    Nationality = ListField(DictField(NationalityModel))
    Title = ListField(DictField(TitleModel))
    Industry = ListField(DictField(IndustryModel))
    Position = ListField(DictField(PositionModel))
    Medium = ListField(DictField(MediumModel))
    Genre = ListField(DictField(GenreModel))
    Interest = ListField(DictField(InterestModel))
    Publisher = ListField(DictField(PublisherModel))
    SourceType = ListField(DictField(SourceTypeModel))
    TopMuseum = ListField(DictField(TopMuseumModel))
    Relation = ListField(DictField(RelationshipTypeModel))
    ArtFair = ListField(DictField(ArtFairModel))

    Network = SOCIAL_NETWORKS
    Gender = GENDER_CHOICES
    DocumentType = DOCUMENT_TYPES
    CollectionPosition = COLLECTION_POSITIONS
    CooperationType = COOPERATION_TYPES
    FeederRole = FEEDER_ROLES
    Ranking = RANKINGS
    RankingYear = YEARS


    ExpiryMonth = MONTHS
    ExpiryYear = EXPIRY_YEARS
    CardType = CARD_TYPES