from bisect import bisect_left
from collections import OrderedDict
from datetime import datetime
from operator import itemgetter
from jsonclient import Mapping, TextField, DictField, ListField, IntegerField
from larryslist.models.address import LocationModel
from larryslist.models.artist import ArtistModel
from pyramid.decorator import reify

__author__ = 'Martin'





class NullConfigModel(Mapping):
    name = TextField()
    def getKey(self, request):return ''
    def getLabel(self, request):return '---'


class NamedModel(Mapping):
    name = TextField()
    def getKey(self, request):return self.name
    def getLabel(self, request):return self.name

    def toQuery(self):
        return {'value':self.name, 'label': self.name}

class NationalityModel(NamedModel): pass
class TitleModel(NamedModel): pass
class IndustryModel(NamedModel): pass
class PositionModel(NamedModel): pass
class EngagementPositionModel(NamedModel): pass
class ArtFairPositionModel(NamedModel): pass
class CollectionPositionModel(NamedModel): pass
class CooperationTypeModel(NamedModel): pass
class RelationshipTypeModel(NamedModel): pass

class InterestModel(NamedModel): pass
class SocNetModel(NamedModel): pass
class MediumModel(NamedModel): pass
class MaterialModel(NamedModel): pass
class GenreModel(NamedModel): pass
class ThemeModel(NamedModel): pass
class OriginModel(NamedModel): pass
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
    country = TextField()
    postCode = TextField()
    line1 = TextField()
    line2 = TextField()
    city = TextField()
    def getLabel(self, request):return u"{0.name} ({0.city})".format(self)
    def getKey(self, request):return self.name



class ReviewedCollectorsModel(Mapping):
    no = IntegerField()






GENDER_CHOICES = [GenderModel(key = 'm', label = 'male'), GenderModel(key = 'f', label = 'female')]
SOCIAL_NETWORKS = [SocNetModel(name = 'Facebook'), SocNetModel(name = 'Linkedin'), SocNetModel(name = 'Twitter'), SocNetModel(name = 'Xing'), SocNetModel(name = 'Weibo'), SocNetModel(name = 'Renren'), SocNetModel(name = 'Other')]
DOCUMENT_TYPES = [DocumentTypeModel(name = 'IMAGE'), DocumentTypeModel(name = 'OTHER')]



RM = RankingModel
RANKINGS = [RM(name="ARTnews"), RM(name="Art & Auction"), RM(name="Art Review")]
FEEDER_ROLES = [FeederRoleModel(name="REVIEWER"), FeederRoleModel(name="OPERATOR")]
YEARS = [NamedModel(name = yr) for yr in range(datetime.now().year, datetime.now().year - 50, -1)]
MONTHS = [NamedModel(name = mon) for mon in range(1, 13)]
EXPIRY_YEARS = [NamedModel(name = yr) for yr in range(datetime.now().year, datetime.now().year + 50)]
CARD_TYPES = [NamedModel(name = 'VISA'), NamedModel(name = 'MC'), NamedModel(name = 'AMEX')]




COOPERATION_TYPES = [dict(name = "Exhibition of own collection"), dict(name = "Sponsoring"), dict(name = "Funding of Award"), dict(name = "Support of educational program")]
ENGAGEMENT_POSITIONS = [{'name':'Trustee'},{'name':'Board Member'},{'name':'Selection Committee'},{'name':'Chairman'},{'name':'President'},{'name':'Founding Chairman'},{'name':'Co-Chair'},{'name':'Life Trustee'},{'name':'Treasurer'}]
ART_FAIR_POSITION = [{'name':'Board Member of Fair'}, {'name':'Panel speaker'}, {'name':'In press release or on webpage mentioned'}, {'name':'Others'}]
COLLECTION_POSITIONS = [{'name':"Director"},{'name':"Curator"},{'name':"Head of Collection"}]


class ConfigModel(Mapping):
    Nationality = ListField(DictField(NationalityModel))
    Title = ListField(DictField(TitleModel))
    Industry = ListField(DictField(IndustryModel))
    Position = ListField(DictField(PositionModel))
    Medium = ListField(DictField(MediumModel))
    Material = ListField(DictField(MaterialModel))
    Genre = ListField(DictField(GenreModel))
    Origin = ListField(DictField(OriginModel))
    Interest = ListField(DictField(InterestModel))
    Publisher = ListField(DictField(PublisherModel))
    SourceType = ListField(DictField(SourceTypeModel))
    TopMuseum = ListField(DictField(TopMuseumModel))
    Relation = ListField(DictField(RelationshipTypeModel))
    ArtFair = ListField(DictField(ArtFairModel))
    Artist = ListField(DictField(ArtistModel))
    City = ListField(DictField(LocationModel))
    Country = ListField(DictField(LocationModel))


    CooperationType = ListField(DictField(CooperationTypeModel))
    EngagementPosition = ListField(DictField(EngagementPositionModel))
    ArtFairPosition = ListField(DictField(ArtFairPositionModel))
    CollectionPosition = ListField(DictField(CollectionPositionModel))

    Network = SOCIAL_NETWORKS
    Gender = GENDER_CHOICES
    DocumentType = DOCUMENT_TYPES

    FeederRole = FEEDER_ROLES
    Ranking = RANKINGS
    RankingYear = YEARS
    ReviewedCollectors = DictField(ReviewedCollectorsModel)

    ExpiryMonth = MONTHS
    ExpiryYear = EXPIRY_YEARS
    CardType = CARD_TYPES

    @reify
    def topMuseumMap(self):
        return {m.name:m for m in self.TopMuseum}


    @reify
    def searchLookups(self):
        return {
            'ARTIST':{str(a.id): a for a in self.Artist}
            , 'CITY': {a.token: a for a in self.City}
            , 'COUNTRY': {c.token: c for c in self.Country}
            , 'MEDIUM': {c.name for c in self.Medium}
            , 'GENRE': {c.name for c in self.Genre}
            , 'ORIGIN': {c.name for c in self.Origin}
        }
    def getArtist(self, id):
        lookup = self.searchLookups['ARTIST']
        try:
            return lookup.get(int(id))
        except TypeError, e:
            return None
    def getCity(self, token):
        lookup = self.searchLookups['CITY']
        return lookup.get(token)
    def getCountry(self, token):
        lookup = self.searchLookups['COUNTRY']
        return lookup.get(token)

    def convertToQuery(self, queryMap):
        query = {}
        for k,v in queryMap.items():
            lookup = self.searchLookups.get(k)
            obj = lookup.get(v)
            if obj:
                query[k] = obj.toQuery()
        return query

    def getFilterSelection(self):
        return {
            'GENDER': [{'value':'f', 'label':'Woman'}, {'value':'m', 'label':'Man'}]
            , 'MEDIUM': [g.toQuery() for g in self.Medium[:5]]
            , 'GENRE': [g.toQuery() for g in self.Genre[:5]]
            , 'COUNTRY': [g.toQuery() for g in self.Country[:5]]
            , 'ORIGIN': [g.toQuery() for g in self.Origin[:5]]
            , 'ARTIST': [g.toQuery() for g in self.Artist[:5]]
            , 'CITY': [g.toQuery() for g in self.City[:5]]
        }
    @reify
    def searchIndex(self):
        return {
            'MEDIUM': OrderedDict(sorted([(g.name.lower(), g) for g in self.Medium]))
            , 'GENRE': OrderedDict(sorted([(g.name.lower(), g) for g in self.Genre]))
            , 'COUNTRY': OrderedDict(sorted([(g.name.lower(), g) for g in self.Country]))
            , 'ORIGIN': OrderedDict(sorted([(g.name.lower(), g)  for g in self.Origin]))
            , 'ARTIST': OrderedDict(sorted([(g.name.lower(), g)  for g in self.Artist]))
            , 'CITY': OrderedDict(sorted([(g.name.lower(), g) for g in self.City]))
        }
    def querySearch(self, query):
        key, word_fragment = query['key'], query['value'].lower()
        if not key or not word_fragment:
            return []
        wordlist = self.searchIndex[key].keys()
        result = wordlist[bisect_left(wordlist, word_fragment):bisect_left(wordlist, word_fragment[:-1] + chr(ord(word_fragment[-1])+1))]
        lookup = self.searchIndex[key]
        return [lookup[r].toQuery() for r in result[:10]]


    @classmethod
    def wrap(cls, data):
        data['CooperationType'] = COOPERATION_TYPES
        data['EngagementPosition'] = ENGAGEMENT_POSITIONS
        data['CollectionPosition'] = COLLECTION_POSITIONS
        data['ArtFairPosition'] = ART_FAIR_POSITION
        return super(ConfigModel, cls).wrap(data)