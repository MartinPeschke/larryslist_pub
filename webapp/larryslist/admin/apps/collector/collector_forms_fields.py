import formencode
from larryslist.lib.formlib.formfields import TokenTypeAheadField, MultipleFormField, StringField, ConfigChoiceField, PictureUploadField, PlainHeadingField, TagSearchField, EmailField, IMPORTANT, URLField, MultiConfigChoiceField, PictureUploadAttrs, REQUIRED, Placeholder, Field, configattr, TextareaField, BaseSchema, HiddenField, HtmlAttrs, ConfigTypeAheadField


class RestrictedCountryField(TokenTypeAheadField):
    template = 'larryslist:admin/templates/collector/country.html'

class AddressForm(MultipleFormField):
    fields = [
        RestrictedCountryField('Country', 'Country', '/admin/search/address', 'AddressSearchResult', None, REQUIRED)
        , TokenTypeAheadField('Region', 'Region', '/admin/search/address', 'AddressSearchResult', 'Country')
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Country Region', REQUIRED)
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
    ]
class UniversityForm(MultipleFormField):
    fields = [
        StringField('name', 'Name of University')
        , StringField('city', 'City')
    ]
collectorCreateFields = [
        StringField('firstName', 'First Name', REQUIRED)
        , StringField('lastName', 'Last Name', REQUIRED)
        , StringField('origName', 'Name in orig. Language')
        , ConfigChoiceField('title', 'Title', 'Title', IMPORTANT)
        , StringField('dob', 'Born', IMPORTANT)
        , ConfigChoiceField('gender', 'Gender', 'Gender', IMPORTANT)
        , ConfigChoiceField('nationality', 'Nationality', 'Nationality', IMPORTANT)
        , PictureUploadField('picture', 'Picture', attrs = PictureUploadAttrs())
        , AddressForm('Address', 'Location')
        , UniversityForm('University', classes = 'form-embedded-wrapper form-inline')
        , PlainHeadingField("Areas of Interest")
        , TagSearchField('Interest', "Interest", "/admin/search/interest", "Interest", api_allow_new = True, classes='tagsearch input-xxlarge')
    ]






class MultiEmailField(MultipleFormField):
    fields = [EmailField('address', 'Email', IMPORTANT, input_classes="input-xlarge")]
class NetworkField(MultipleFormField):
    fields = [ConfigChoiceField('name', None, 'Network', default_none = False), URLField('url', '', attrs = Placeholder("link"))]
collectorContactsFields = [
        URLField('wikipedia', 'Wikipedia', IMPORTANT, input_classes="input-xlarge")
        , MultiEmailField('Email', None)
        , PlainHeadingField("Social networks")
        , NetworkField("Network", classes = "form-controls-inline form-inline form-embedded-wrapper")
    ]









class CompanyForm(MultipleFormField):
    """
        "name": "ESSO", "position": "CEO and Founder", "industry": "Automotive", "url": "http://esso.com", "city": "Berlin", "postCode": "BN3 1BA", "line1": "1 the av" },
    """
    fields = [
        StringField("name", "Name of company")
        , ConfigChoiceField("position", "Position", "Position")
        , ConfigChoiceField("industry", "Industry", "Industry")
        , URLField("url", "Link")
        , PlainHeadingField("Location", tag="span", classes = "heading-absolute")
        , TokenTypeAheadField('Country', 'Country', '/admin/search/address', 'AddressSearchResult', None)
        , TokenTypeAheadField('Region', 'Region', '/admin/search/address', 'AddressSearchResult', 'Country')
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Country Region')
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
    ]

collectorBusinessFields = [
        CompanyForm("Company")
        , PlainHeadingField('Further industries / type of businesses')
        , MultiConfigChoiceField('name', 'Name', "Industry", "Industry", attrs = REQUIRED)
    ]
collectionAddCollectorForm = [ConfigChoiceField("relation", "Relationship", "Relation", attrs = REQUIRED)] + collectorCreateFields + [HiddenField('collectionId')]





class TypedFileUploadField(Field):
    template = 'larryslist:admin/templates/collector/typed_file_upload.html'
    add_more_link_label = '+'
    if_empty = {}
    def __init__(self, name, classes = 'form-embedded-wrapper'):
        self.name = name
        self.classes = classes
        self.optionGetter = configattr('DocumentType', default_none=True)
    def getClasses(self):
        return self.classes
    def getValidator(self, request):
        validators = {}
        return {self.name : formencode.ForEach(BaseSchema(type = formencode.validators.String(), file = formencode.validators.String(), name=formencode.validators.String()), not_empty = self.attrs.required)}
    def getOptions(self, request):
        return self.optionGetter(request)
    TYPES = {'IMAGE': "jpg,gif,png", 'OTHER': "*.*"}
    def getFileTypes(self, dt):
        return self.TYPES.get(dt.name, 'DISABLED')

class ArbitraryURLAttachmentsFields(MultipleFormField):
    fields = [URLField("url", "URL")]

collectorUploadFields = [
        PlainHeadingField("Collector Documents")
        , TypedFileUploadField("Document", classes = 'form-embedded-wrapper form-inline')
        , PlainHeadingField("Collector relevant URLs")
        , ArbitraryURLAttachmentsFields("Attachments")
    ]





class MuseumForm(MultipleFormField):
    fields = [
        ConfigChoiceField("museum", "Top 100 Museum", "TopMuseum", attrs = HtmlAttrs(**{'data-custom-module':'views/museum'}),  input_classes="custom-control")
        , StringField("other_name", "Not Top 100 Museum, then name", label_classes='double')
        , ConfigTypeAheadField('position', 'Position', 'EngagementPosition')
        , StringField("year", "Year")
        , URLField("website", "Website")
        , PlainHeadingField("Location", tag="h5", classes="controls")
        , TokenTypeAheadField('Country', 'Country', '/admin/search/address', 'AddressSearchResult', None)
        , TokenTypeAheadField('Region', 'Region', '/admin/search/address', 'AddressSearchResult', 'Country')
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Country Region')
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
    ]

class SocietyMemberForm(MultipleFormField):
    fields = [
        StringField("societyName", "Name of society")
        , URLField("website", "Website")
        , ConfigTypeAheadField("position", "Position", "EngagementPosition")
        , PlainHeadingField("Location", tag="h5", classes="controls")
        , TokenTypeAheadField('Country', 'Country', '/admin/search/address', 'AddressSearchResult', None)
        , TokenTypeAheadField('Region', 'Region', '/admin/search/address', 'AddressSearchResult', 'Country')
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Country Region')
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
    ]

collectorArtAdvisoryFields = [
        PlainHeadingField("Collector is in Advisory board, a committee member, a trustee in art expert juries of a public art institution / museum")
        , MuseumForm("Museum")
        , PlainHeadingField("Collector is member of an art society, friends circle of museums etc.")
        , SocietyMemberForm("SocietyMember")
    ]





class OtherFactForm(MultipleFormField):
    fields=[TextareaField('value', "Fact", input_classes="span10")]
collectorOtherFactsFields = [PlainHeadingField("Other Facts"), OtherFactForm("Fact")]








class RankingForm(MultipleFormField):
    fields = [
        ConfigChoiceField("name", "Ranking", "Ranking")
        , ConfigChoiceField("year", "Year", "RankingYear")
    ]
collectorRankingFields = [
        PlainHeadingField("Ranking")
        , PlainHeadingField("Collector was named in the ranking in the year", tag="p")
        , RankingForm("Ranking", classes = 'form-embedded-wrapper form-inline')
    ]

class ArtFairForm(MultipleFormField):
    fields = [
        ConfigTypeAheadField("name", "Art Fair", "ArtFair")
        , ConfigChoiceField("position", "Position", 'ArtFairPosition')
        , ConfigChoiceField("year", "Year", "RankingYear")
    ]
collectorArtFairFields = [
    PlainHeadingField("Collector mentioned at art fair")
    , PlainHeadingField("(at fair's webpage, art fair's press release, participated on the art fair's panel or member of fair's board)", tag="p")
    , ArtFairForm("ArtFair", classes = 'form-embedded-wrapper form-inline')
]