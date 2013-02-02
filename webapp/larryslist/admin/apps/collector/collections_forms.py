from jsonclient.backend import DBException
import formencode
from larryslist.admin.apps.collector.collector_forms import TypedFileUploadField
from larryslist.admin.apps.collector.models import CreateCollectionProc, EditCollectionBaseProc, EditCollectionArtistsProc, EditCollectionPublicationsProc, SaveCollectionDocumentsProc
from larryslist.admin.apps.collector.sources_form import BaseAdminForm
from larryslist.lib.formlib.formfields import BaseForm, IntField, CheckboxField, IMPORTANT, StringField, MultiConfigChoiceField, ApproxField, HiddenField, MultipleFormField, TypeAheadField, PlainHeadingField, ConfigChoiceField, URLField, TagSearchField, BaseSchema, Placeholder, TokenTypeAheadField, REQUIRED

__author__ = 'Martin'


class BaseCollectionForm(BaseAdminForm):
    id = 'basic'
    label = 'Basic'
    fields = [
        ApproxField('totalWorks', 'totalWorksAprx', "Total number of artworks in collection", IMPORTANT, label_classes="double")
        , ApproxField('totalArtists', 'totalArtistsAprx', "Total number of artists in collection", IMPORTANT, label_classes="double")
        , StringField("name", "Name of collection", IMPORTANT)
        , StringField("foundation", "Name of foundation")
        , IntField('started', "Started collecting in year")
        , PlainHeadingField("Themes in collection")
        , TagSearchField('Theme', "Tags", "/admin/search/theme", "Theme", api_allow_new = True, classes='tagsearch input-xxlarge')
        , PlainHeadingField("Art Genre / Movement")
        , MultiConfigChoiceField('name', 'Name', "Genre", "Genre")
        , PlainHeadingField("Medium of artworks")
        , MultiConfigChoiceField('name', 'Name', "Medium", "Medium")
        , PlainHeadingField("Region of interest")
        , TagSearchField('Origin', "Tags", "/admin/search/origin", "Origin", api_allow_new = False, classes='tagsearch input-xxlarge')
    ]

    @classmethod
    def persist(cls, request, values):
        collectorId = request.matchdict['collectorId']
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = CreateCollectionProc(request, values)
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'redirect': request.fwd_url("admin_collection_edit", collectorId = collectorId, stage='basic')}


class CollectionEditForm(BaseCollectionForm):
    fields = BaseCollectionForm.fields  + [
            HiddenField('id')
        ]
    @classmethod
    def persist(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = EditCollectionBaseProc(request, values)
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}


class MultipleArtistField(TagSearchField):
    if_empty = []
    template = 'larryslist:admin/templates/collector/artist.html'
    def getValidator(self, request):
        return {self.name : formencode.ForEach(BaseSchema(id = formencode.validators.String(if_missing = None)), not_empty = self.attrs.required)}
class CollectionArtistsForm(BaseAdminForm):
    id = 'artist'
    label = 'Artists'
    fields = [
        HiddenField('id')
        , PlainHeadingField("Artists in Collection")
        , MultipleArtistField('Artist', "Artist", "/admin/search/artist", "Artist", attrs = Placeholder("Search for an Artist"), input_classes="input-xxlarge")
    ]

    @classmethod
    def persist(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = EditCollectionArtistsProc(request, values)
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}



class PublicationsForm(MultipleFormField):
    fields = [
        StringField('title', "Title")
        , ConfigChoiceField('publisher', 'Publisher', 'Publisher')
        , IntField('year', "Year")
    ]
class CollectionWebsiteForm(BaseAdminForm):
    id = 'website'
    label = 'Communication Platforms'
    fields = [
        HiddenField('id')
        , PlainHeadingField("Website")
        , URLField('url', "Webpage", attrs = IMPORTANT)
        , PlainHeadingField("Publications")
        , PublicationsForm('Publication', "", classes = "form-embedded-wrapper form-inline")
    ]

    @classmethod
    def persist(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection': values}
        try:
            collection = EditCollectionPublicationsProc(request, values)
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}


class CollectionUploadForm(BaseAdminForm):
    id = "uploads"
    label = "Uploads"
    fields = [
        PlainHeadingField("Collection Documents")
        , TypedFileUploadField("Document", classes = 'form-embedded-wrapper form-inline')
        , HiddenField('id')
    ]
    @classmethod
    def persist(cls, request, values):
        try:
            data = {'id':request.matchdict['collectorId'], 'Collection': values}
            collector = SaveCollectionDocumentsProc(request, {'Collection':data})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}



class MuseumForm(MultipleFormField):
    fields = [
        CheckboxField("has_space", "Has permanent museum/space")
        , StringField("name", "If yes, name")
        , StringField("year", "Founded in year")
        , StringField("website", "Webpage")
        , TokenTypeAheadField('Country', 'Country', '/admin/search/address', 'AddressSearchResult', None, REQUIRED)
        , TokenTypeAheadField('Region', 'Region', '/admin/search/address', 'AddressSearchResult', 'Country')
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Country Region', REQUIRED)
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
        , StringField('phone', 'Telephone')
    ]
class PositionForm(MultipleFormField):
    fields = [
        ConfigChoiceField('position', 'Position', 'CollectionPosition')
        , StringField("lastName", "Last Name")
        , StringField("firstName", "First Name")
        , StringField("origName", "Name in orig. Language")
        , ConfigChoiceField('title', 'Title', 'Title')
        , ConfigChoiceField('gender', 'Gender', 'Gender')
        , StringField("email", "Contact Email")
        , URLField("facebook", "Contact Facebook", input_classes = 'input-large')
        , URLField("linkedin", "Contact Linked-in", input_classes = 'input-large')
    ]


class CollectionMuseumForm(BaseAdminForm):
    template = "larryslist:admin/templates/collector/splitform.html"
    id = 'museum'
    label = 'Museum'
    separateAfter = 2
    fields = [
        PlainHeadingField("Permanent museum or exhibition space")
        , MuseumForm('Museum')
        , PlainHeadingField("Director or curator or head of collection (internal)")
        , PositionForm("Director")
    ]


class LoanForm(MultipleFormField):
    fields = [
        StringField("name", "What donated / on loan")
        , StringField("comment", "Comment")
        , StringField("year", "Year")
        , StringField("institution", "Name of institution")
        , TokenTypeAheadField('Country', 'Country', '/admin/search/address', 'AddressSearchResult', None, REQUIRED)
        , TokenTypeAheadField('Region', 'Region', '/admin/search/address', 'AddressSearchResult', 'Country')
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Country Region', REQUIRED)
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
    ]
class CooperationForm(MultipleFormField):
    fields = [
        ConfigChoiceField('type', "Type of Cooperation", "CooperationType")
        , StringField("comment", "Name of cooperation / Comment")
        , StringField("year", "Year")
        , StringField("institution", "Name of institution")
        , TokenTypeAheadField('Country', 'Country', '/admin/search/address', 'AddressSearchResult', None, REQUIRED)
        , TokenTypeAheadField('Region', 'Region', '/admin/search/address', 'AddressSearchResult', 'Country')
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Country Region', REQUIRED)
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
    ]


class CollectionCooperationForm(BaseAdminForm):
    template = "larryslist:admin/templates/collector/splitform.html"
    id="cooperation"
    label = "Cooperation"
    separateAfter = 2
    fields = [
        PlainHeadingField("Permanent loan / donation of artworks to museum")
        , LoanForm('Loan')
        , PlainHeadingField("Cooperation with external museums / institutions")
        , PlainHeadingField("(e.g. exhibition with part of the collector's private collection)", tag="p")
        , CooperationForm("Cooperation")
    ]