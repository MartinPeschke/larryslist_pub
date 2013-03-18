from jsonclient import TextField, Mapping, DateField, IntegerField, BooleanField, DictField, ListField, DateTimeField
from jsonclient.backend import RemoteProc
from larryslist.models.config import GenreModel, MediumModel, NamedModel, InterestModel, IndustryModel, ThemeModel, OriginModel
from pyramid.decorator import reify



class LocationModel(Mapping):
    name = TextField()
    token = TextField()

class AddressModel(Mapping):
    line1 = TextField()
    line2 = TextField()
    line3 = TextField()
    postCode = TextField()
    Country = DictField(LocationModel)
    Region = DictField(LocationModel)
    City = DictField(LocationModel)
    website = TextField()

    def getLines(self, request):
        return '<br/>'.join([getattr(self, v) for v in ['line1', 'line2', 'line3'] if getattr(self, v, None)])

    def getCityPostCode(self, request):
        if self.postCode and self.City:
            return u'{}, {}'.format(self.City.name, self.postCode)
        elif self.postCode:
            return self.postCode
        elif self.City:
            return self.City.name
        else:
            return ''

    def getRegion(self, request):
        return self.Region.name if self.Region else ''

    def getCountry(self, request):
        return self.Country.name if self.Country else ''

class SimpleCollectorModel(Mapping):
    id = IntegerField()
    status = TextField()
    updated = DateTimeField()
    initials = TextField()
    picture = TextField()
    ranking = TextField(default = 0)
    followers = TextField(default = 0)
    completness = TextField(default = 0)
    Address = ListField(DictField(AddressModel))
    def getName(self):
        return self.initials
    def getAddress(self):
        if not len(self.Address): return ''
        addr = self.Address[0]
        if not addr.Region or not addr.Country: return ''
        return u"{region}, {country}".format(region = addr.Region.name, country = addr.Country.name)
    def getUpdated(self):
        if self.updated:
            return '{:0>2}/{}'.format(self.updated.month, self.updated.year)
        else:
            return ''

    def getRank(self):
        return "#{}".format(self.ranking)
    def getSubscribers(self):
        return self.followers
    def getCompletion(self):
        return self.completness



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
    date = TextField()
    year = TextField()
    publisher = TextField()

    def isURL(self):
        return self.type == 'Internet/Blogs/Online Mag'

    def getSourceLine(self):
        fields = ['url', 'name', 'title', 'author', 'publisher', 'year', 'date']
        return ', '.join([getattr(self, k) for k in fields if getattr(self, k, None)])

class ArtworkModel(Mapping):
    title = TextField()
    year = TextField()
    material = TextField()
    medium = TextField()
    width = IntegerField()
    height = IntegerField()
    depth = IntegerField()
    measurement = TextField()

    def getMeasure(self):
        return 'cm' if self.measurement == 'METRIC' else 'in'
    @reify
    def size(self):
        m = ''
        if self.width:
            m += u'w: {} '.format(self.width)
        if self.height:
            m += u'h: {} '.format(self.height)
        if self.depth:
            m += u'd: {} '.format(self.depth)
        if m: m += self.getMeasure()
        return m



    def getLabel(self, request):
        if self.year:
            return u'{} ({})'.format(self.title, self.year)
        else:
            return self.title


class ArtistModel(Mapping):
    name = TextField()
    year = TextField()
    ArtWork = ListField(DictField(ArtworkModel))
    def getLabel(self, request):
        if self.year:
            return u'{} ({})'.format(self.name, self.year)
        else:
            return self.name

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
    url = TextField()
    year = TextField()
    started = TextField()
    Genre = ListField(DictField(GenreModel))
    Theme = ListField(DictField(ThemeModel))
    Medium = ListField(DictField(MediumModel))
    Origin = ListField(DictField(OriginModel))

    Artist = ListField(DictField(ArtistModel))
    Region = ListField(DictField(CollectionRegionModel))
    Publisher = ListField(DictField(PublisherModel))

    def getNoArtists(self):
        if self.totalArtistsAprx:
            return u'>{}'.format(self.totalArtists)
        else:
            return unicode(self.totalArtists or 'Unknown')

    def getNoArtworks(self):
        if self.totalWorksAprx:
            return u'>{}'.format(self.totalWorks)
        else:
            return unicode(self.totalWorks or 'Unknown')
    def hasArtists(self):
        return len(self.Artist) > 0

    def hasArtworks(self):
        return len(self.Artist) > 0

class UniversityModel(Mapping):
    name = TextField()
    city = TextField()
    def getLabel(self, request):
        if self.city:
            return u'{0.name}, {0.city}'.format(self)
        else:
            return self.name

class EmailModel(Mapping):
    address = TextField()
    def getLabel(self, request):
        return self.address

class NetworkModel(Mapping):
    ICONS = {
        'Facebook':'icon icon-facebook'
        ,'Twitter':'icon icon-twitter'
        ,'Linkedin':'icon icon-linkedin'
    }
    name = TextField()
    url = TextField()
    def getLabel(self, request):
        return self.name
    def getIcon(self, request):
        return self.ICONS.get(self.name, 'no-icon')
    def getAddress(self, request):
        return self.url


class CompanyModel(AddressModel):
    name = TextField()
    position = TextField()
    industry = TextField()
    website = TextField(name = 'url')

class LinkedCollectorModel(Mapping):
    id = IntegerField()
    firstName = TextField()
    lastName = TextField()
    relation = TextField()
    def getName(self):
        result = u'{0.firstName} {0.lastName}'.format(self)
        if self.relation:
            result += u" ({})".format(self.relation)
        return result

class OtherFactModel(Mapping):
    value = TextField()

STATUS = {
    'INPROGRESS':"In Progress"
    ,'SUBMITTED':"Submitted"
    ,'REVIEWED':"Reviewed"
}

class CollectorModel(SimpleCollectorModel):

    feederName = TextField()
    firstName = TextField()
    lastName = TextField()
    origName = TextField()
    dob = TextField()
    nationality = TextField()
    Title = TextField()
    Gender = TextField()
    wikipedia = TextField()
    Interest = ListField(DictField(InterestModel))
    Email = ListField(DictField(EmailModel))

    Network = ListField(DictField(NetworkModel))
    Company = ListField(DictField(CompanyModel))
    Industry = ListField(DictField(IndustryModel))
    University = ListField(DictField(UniversityModel))
    Collection = DictField(CollectionModel)
    Source = ListField(DictField(SourceModel))
    LinkedCollector = DictField(LinkedCollectorModel)
    Fact = ListField(DictField(OtherFactModel))

    def getName(self):
        return u'{firstName} {lastName}'.format(firstName = self.firstName, lastName = self.lastName)
    def getStatusLabel(self):
        return STATUS[self.status]
    def canSubmitforReview(self, user):
        return self.status == 'INPROGRESS'
    def canReview(self, user):
        return self.status == 'SUBMITTED' and user.isAdmin()
    def isSubmitted(self):
        return self.status == 'SUBMITTED'
    def isReviewed(self):
        return self.status == 'REVIEWED'
    def getGenreList(self):
        if self.Collection:
            return ', '.join([g.name for g in self.Collection.Genre])
        else:
            return ''
    def getPicture(self):
        return self.picture or "http://www.gravatar.com/avatar/00000000000000000000000000000000?d=mm&s=200"


    def getDOB(self, request):
        return self.dob


    def hasFacts(self):
        return len(self.Fact) > 0
    def hasBusiness(self):
        return len(self.Company) + len(self.Industry) > 0


class MetaRemoteProc(RemoteProc):
    def __init__(self, remote_path, auth_extractor):
        super(MetaRemoteProc, self).__init__(remote_path, "POST", 'json')
        self.auth_extractor = auth_extractor
    def __call__(self, request, id, data = {}):
        backend = request.backend
        result = self.call(backend, data, headers = self.auth_extractor(request, id, data))
        return result if result else {}
def MetaDataProc(path):
    def auth_extractor(request, id, data = {}):
        return {'Client-Token':request.root.settings.clientToken, 'JsonObjectId':id}
    return MetaRemoteProc(path, auth_extractor)

GetCollectorMetaProc = MetaDataProc("/admin/collector/meta")
GetCollectionMetaProc = MetaDataProc("/admin/collection/meta")





class MuseumModel(AddressModel):
    telephone = TextField()
    year = TextField()
    url = TextField()
    permanentSpace = TextField()
    website = url

class DirectorModel(Mapping):
    id = IntegerField()
    firstName = TextField()
    lastName = TextField()
    origName = TextField()
    title = TextField()
    gender = TextField()
    position = TextField()
    email = TextField()
    facebook = TextField()
    linkedin = TextField()
    def getLabel(self, request):
        return u'{} {}'.format(self.firstName, self.lastName)

class ArtAdvisorModel(Mapping):
    lastName = TextField()
    firstName = TextField()
    origName = TextField()
    title = TextField()
    gender = TextField()
    company = TextField()
    email = TextField()
    facebook = TextField()
    linkedin = TextField()
    def getLabel(self, request):
        return u'{} {}'.format(self.firstName, self.lastName)

class PublicationModel(Mapping):
    title = TextField()
    publisher = TextField()
    year = TextField()

class LoanModel(AddressModel):
    name = TextField()
    comment = TextField()
    year = TextField()
    institution = TextField()

class CooperationModel(AddressModel):
    type = TextField()
    comment = TextField()
    year = TextField()
    institution = TextField()

class CollectionMetaModel(Mapping):
    Museum = ListField(DictField(MuseumModel))
    Director = ListField(DictField(DirectorModel))
    Publication = ListField(DictField(PublicationModel))
    ArtAdvisor = ListField(DictField(ArtAdvisorModel))
    Loan = ListField(DictField(LoanModel))
    Cooperation = ListField(DictField(CooperationModel))
    def getDenseList(self, list):
        return [l for l in list if isinstance(l, Mapping) and not l.isEmptyModel()]



class BoardMemberModel(AddressModel):
    museum = TextField()
    other_name = TextField()
    position = TextField()
    year = TextField()

    def getMusem(self, request):
        if not getattr(self, 'topMuseum', None):
            setattr(self, 'topMuseum', request.root.config.topMuseumMap.get(self.museum))
        return self.topMuseum

    def getLines(self, request):
        if self.museum and self.getMusem(request):
            museum = self.getMusem(request)
            return '<br/>'.join([getattr(museum, v) for v in ['line1', 'line2'] if getattr(museum, v, None)])
        return super(BoardMemberModel, self).getLines(request)

    def getCityPostCode(self, request):
        if self.museum and self.getMusem(request):
            museum = self.getMusem(request)
            return u'{}, {}'.format(museum.city, museum.postCode)
        return super(BoardMemberModel, self).getCityPostCode(request)

    def getRegion(self, request):
        if self.museum and self.getMusem(request): return ''
        return super(BoardMemberModel, self).getRegion(request)

    def getCountry(self, request):
        if self.museum and self.getMusem(request):
            museum = self.getMusem(request)
            return museum.country or ''
        return super(BoardMemberModel, self).getCountry(request)

class SocietyMemberModel(AddressModel):
    societyName = TextField()
    position = TextField()
    year = TextField()

class CollectorMetaModel(Mapping):
    Museum = ListField(DictField(BoardMemberModel))
    SocietyMember = ListField(DictField(SocietyMemberModel))
    def getDenseList(self, list):
        return [l for l in list if isinstance(l, Mapping) and not l.isEmptyModel()]
