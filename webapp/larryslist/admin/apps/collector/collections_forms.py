from jsonclient.backend import DBException
import formencode
from larryslist.admin.apps.collector.collector_forms import TypedFileUploadField
from larryslist.admin.apps.collector.models import CreateCollectionProc, EditCollectionBaseProc, EditCollectionArtistsProc, EditCollectionPublicationsProc, SaveCollectionDocumentsProc, SaveCollectionMuseumProc, GetCollectionMetaProc
from larryslist.admin.apps.collector.sources_form import BaseAdminForm
from larryslist.lib.formlib.formfields import BaseForm, IntField, CheckboxField, IMPORTANT, StringField, MultiConfigChoiceField, ApproxField, HiddenField, MultipleFormField, TypeAheadField, PlainHeadingField, ConfigChoiceField, URLField, TagSearchField, BaseSchema, Placeholder, TokenTypeAheadField, REQUIRED, EmailField, RadioChoice
from larryslist.models.config import NamedModel

__author__ = 'Martin'


def collectionData(cls, view):
    return view.collection.unwrap(sparse = True) if view.collection else {}
def collectionMeta(cls, view):
    if view.collection:
        result = GetCollectionMetaProc(view.request, str(view.collection.id))
        result['id'] = view.collection.id
        return result
    else:
        return {}
def persistCollectionMeta(cls, request, values):
    id = values['id']
    cls.setCollectionMeta(request, id, values)
    return {'success': True, 'message':"Changes saved!"}



class BaseCollectionForm(BaseAdminForm):
    id = 'basic'
    label = 'Basic'
    getFormValues = classmethod(collectionData)
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
    getFormValues = classmethod(collectionData)
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
    getFormValues = classmethod(collectionData)
    fields = [
        HiddenField('id')
        , PlainHeadingField("Website")
        , URLField('url', "URL", attrs = IMPORTANT)
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
    getFormValues = classmethod(collectionData)
    fields = [
        PlainHeadingField("Collection Documents")
        , TypedFileUploadField("Document", classes = 'form-embedded-wrapper form-inline')
        , HiddenField('id')
    ]
    @classmethod
    def persist(cls, request, values):
        try:
            data = {'id':request.matchdict['collectorId'], 'Collection': values}
            collector = SaveCollectionDocumentsProc(request, {'Collector':data})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}


class MuseumForm(MultipleFormField):
    fields = [
        StringField("Permanent museum/space name", "If yes, name", label_classes = 'double')
        , StringField("year", "Founded in year")
        , StringField("url", "Webpage")
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

    @classmethod
    def persist(cls, request, values):
        try:
            data = {'id':request.matchdict['collectorId'], 'Collection': values}
            collector = SaveCollectionMuseumProc(request, {'Collector':data})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}

class CollectionMuseumForm(BaseAdminForm):
    id = 'museum'
    label = 'Museum'
    getFormValues = classmethod(collectionMeta)
    persist = classmethod(persistCollectionMeta)
    fields = [
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
        ConfigChoiceField('type', "Type of Cooperation", "CooperationType")
        , StringField("comment", "Name of cooperation / Comment", label_classes="double")
        , StringField("year", "Year")
        , StringField("institution", "Name of institution")
        , PlainHeadingField("Location", tag="h5", classes="controls")
        , TokenTypeAheadField('Country', 'Country', '/admin/search/address', 'AddressSearchResult', None)
        , TokenTypeAheadField('Region', 'Region', '/admin/search/address', 'AddressSearchResult', 'Country')
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Country Region')
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
    ]
class CollectionCooperationForm(BaseAdminForm):
    id="cooperation"
    label = "Cooperation"
    getFormValues = classmethod(collectionMeta)
    persist = classmethod(persistCollectionMeta)
    fields = [
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
class CollectionArtAdvisor(BaseAdminForm):
    id="artadvisor"
    label = "Art Advisor"
    getFormValues = classmethod(collectionMeta)
    persist = classmethod(persistCollectionMeta)
    fields = [
        PlainHeadingField("External Art Advisor")
        , PlainHeadingField("(independent advisor; not employed at collector's museum)", tag="p")
        , ArtAdvisorForm("ArtAdvisor")
        , HiddenField('id')
    ]