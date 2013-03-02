from jsonclient import TextField, Mapping, DateField, IntegerField, BooleanField, DictField, ListField, DateTimeField
from larryslist.models.config import GenreModel, MediumModel, NamedModel, InterestModel


class LocationModel(Mapping):
    name = TextField()
    token = TextField()

class AddressModel(Mapping):
    line1 = TextField()
    postCode = TextField()
    Country = DictField(LocationModel)
    Region = DictField(LocationModel)
    City = DictField(LocationModel)

class SimpleCollectorModel(Mapping):
    id = IntegerField()
    status = TextField()
    updated = DateTimeField()
    initials = TextField()
    picture = TextField()
    rank = TextField(default = 0)
    subscribers = TextField(default = 0)
    completion = TextField(default = 0)
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
        return self.rank
    def getSubscribers(self):
        return self.subscribers
    def getCompletion(self):
        return u'{}%'.format(self.completion)



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
    name = TextField()
    url = TextField()
    def getLabel(self, request):
        return self.name
    def getIcon(self, request):
        return self.name
    def getAddress(self, request):
        return self.url


class LinkedCollectorModel(Mapping):
    id = IntegerField()
    firstName = TextField()
    lastName = TextField()
    relation = TextField()
    def getName(self):
        result = u'{0.firstName} {0.lastName}'.format(self)
        if self.relation:
            result += u"({})".format(self.relation)
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
    Interest = ListField(DictField(InterestModel))
    Email = ListField(DictField(EmailModel))

    Network = ListField(DictField(NetworkModel))


    University = ListField(DictField(UniversityModel))
    Collection = DictField(CollectionModel)
    Source = DictField(SourceModel)
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
        return ', '.join([g.name for g in self.Collection.Genre])



    def getDOB(self, request):
        return self.dob