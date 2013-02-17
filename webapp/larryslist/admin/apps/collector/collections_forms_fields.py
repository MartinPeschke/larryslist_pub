import formencode
from larryslist.admin.apps.collector.collector_forms_fields import TypedFileUploadField, ArbitraryURLAttachmentsFields
from larryslist.lib.formlib.formfields import IntField, IMPORTANT, StringField, ApproxField, HiddenField, MultipleFormField, PlainHeadingField, ConfigChoiceField, URLField, TagSearchField, BaseSchema, Placeholder, TokenTypeAheadField, EmailField, ConfigTypeAheadField

__author__ = 'Martin'


baseCollectionFields = [
        ApproxField('totalWorks', 'totalWorksAprx', "Total number of artworks in collection", IMPORTANT, label_classes="double")
        , ApproxField('totalArtists', 'totalArtistsAprx', "Total number of artists in collection", IMPORTANT, label_classes="double")
        , StringField("name", "Name of collection", IMPORTANT)
        , StringField("foundation", "Name of foundation")
        , IntField('started', "Started collecting in year")
        , PlainHeadingField("Themes in collection")
        , TagSearchField('Theme', "Tags", "/admin/search/theme", "Theme", api_allow_new = True, classes='tagsearch input-xxlarge')
        , PlainHeadingField("Art Genre / Movement")
        , TagSearchField('Genre', "Genre", "/admin/search/genre", "Genre", api_allow_new = False, classes='tagsearch input-xxlarge tagsearch-required', group_classes='tagsearch-required')
        , PlainHeadingField("Medium of artworks")
        , TagSearchField('Medium', "Medium", "/admin/search/medium", "Medium", api_allow_new = False, classes='tagsearch input-xxlarge')
        , PlainHeadingField("Region of interest")
        , TagSearchField('Origin', "Tags", "/admin/search/origin", "Origin", api_allow_new = False, classes='tagsearch input-xxlarge')
    ]

collectionEditFields = baseCollectionFields  + [HiddenField('id')]


class MultipleArtistField(TagSearchField):
    if_empty = []
    template = 'larryslist:admin/templates/collector/artist.html'
    def getValidator(self, request):
        return {self.name : formencode.ForEach(BaseSchema(id = formencode.validators.String(if_missing = None)), not_empty = self.attrs.required)}
collectionArtistsFields = [
        HiddenField('id')
        , PlainHeadingField("Artists in Collection")
        , MultipleArtistField('Artist', "Artist", "/admin/search/artist", "Artist", attrs = Placeholder("Search for an Artist"), input_classes="input-xxlarge")
    ]

class PublicationsForm(MultipleFormField):
    fields = [
        StringField('title', "Title")
        , ConfigTypeAheadField('publisher', 'Publisher', 'Publisher')
        , IntField('year', "Year")
    ]
collectionWebsiteFields = [
        HiddenField('id')
        , PlainHeadingField("Website")
        , URLField('url', "URL", attrs = IMPORTANT)
        , PlainHeadingField("Publications")
        , PublicationsForm('Publication', "", classes = "form-embedded-wrapper form-inline")
    ]


collectionUploadFields = [
        PlainHeadingField("Collection Documents")
        , TypedFileUploadField("Document", classes = 'form-embedded-wrapper form-inline')
        , PlainHeadingField("Collection relevant URLs")
        , ArbitraryURLAttachmentsFields("Attachments")
        , HiddenField('id')
    ]

class MuseumForm(MultipleFormField):
    fields = [
        StringField("Permanent museum/space name", "If yes, name", label_classes = 'double')
        , StringField("year", "Founded in year")
        , StringField("url", "Website")
        , PlainHeadingField("Location", tag="h5", classes="controls")
        , TokenTypeAheadField('Country', 'Country', '/admin/search/address', 'AddressSearchResult', None)
        , TokenTypeAheadField('Region', 'Region', '/admin/search/address', 'AddressSearchResult', 'Country')
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Country Region')
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
        , StringField('telephone', 'Telephone')
    ]
class DirectorForm(MultipleFormField):
    fields = [
        ConfigChoiceField('position', 'Position', 'CollectionPosition')
        , StringField("lastName", "Last Name")
        , StringField("firstName", "First Name")
        , StringField("origName", "Name in orig. Language")
        , ConfigChoiceField('title', 'Title', 'Title')
        , ConfigChoiceField('gender', 'Gender', 'Gender')
        , PlainHeadingField("Contact", tag="h5", classes="controls")
        , EmailField("email", "Email")
        , URLField("facebook", "Facebook", input_classes = 'input-large')
        , URLField("linkedin", "Linked-in", input_classes = 'input-large')
        , HiddenField('id')
    ]

collectionMuseumFields = [
        PlainHeadingField("Permanent museum or exhibition space")
        , MuseumForm('Museum')
        , PlainHeadingField("Director or curator or head of collection (internal)")
        , DirectorForm("Director")
        , HiddenField('id')
    ]


class LoanForm(MultipleFormField):
    fields = [
        StringField("name", "What donated / on loan")
        , StringField("comment", "Comment")
        , StringField("year", "Year")
        , StringField("institution", "Name of institution")
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
class CooperationForm(MultipleFormField):
    fields = [
        ConfigTypeAheadField('type', "Type of Cooperation", "CooperationType")
        , StringField("comment", "Name of cooperation / Comment", label_classes="double")
        , StringField("year", "Year")
        , StringField("institution", "Name of institution")
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
collectionCooperationFields = [
        PlainHeadingField("Permanent loan / donation of artworks to museum")
        , LoanForm('Loan')
        , PlainHeadingField("Cooperation with external museums / institutions")
        , PlainHeadingField("(e.g. exhibition with part of the collector's private collection)", tag="p")
        , CooperationForm("Cooperation")
        , HiddenField('id')
    ]



class ArtAdvisorForm(MultipleFormField):
    fields = [
        StringField("lastName", "Last Name")
        , StringField("firstName", "First Name")
        , StringField("origName", "Name in orig. Language")
        , ConfigChoiceField('title', 'Title', 'Title')
        , ConfigChoiceField('gender', 'Gender', 'Gender')
        , StringField("company", "Company")
        , PlainHeadingField("Contact", tag="h5", classes="controls")
        , EmailField("email", "Email")
        , URLField("facebook", "Facebook", input_classes = 'input-large')
        , URLField("linkedin", "Linked-in", input_classes = 'input-large')
    ]
collectionArtAdvisorFields = [
        PlainHeadingField("External Art Advisor")
        , PlainHeadingField("(independent advisor; not employed at collector's museum)", tag="p")
        , ArtAdvisorForm("ArtAdvisor")
        , HiddenField('id')
    ]