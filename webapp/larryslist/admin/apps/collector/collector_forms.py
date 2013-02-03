from operator import itemgetter
from jsonclient.backend import DBException
import formencode
from larryslist.admin.apps.collector.models import CreateCollectorProc, EditCollectorBaseProc, EditCollectorContactsProc, EditCollectorBusinessProc, SaveCollectionDocumentsProc, SaveCollectorDocumentsProc, SaveCollectorOtherFactsProc, GetCollectorMetaProc, GetCollectionMetaProc, CollectorModel
from larryslist.admin.apps.collector.sources_form import SingleSourceForm, BaseAdminForm
from larryslist.lib.formlib.formfields import REQUIRED, StringField, BaseForm, ChoiceField, configattr, ConfigChoiceField, DateField, MultipleFormField, IMPORTANT, TypeAheadField, EmailField, HeadingField, URLField, PlainHeadingField, StaticHiddenField, MultiConfigChoiceField, TokenTypeAheadField, HiddenField, Placeholder, PictureUploadField, PictureUploadAttrs, BaseSchema, Field, TextareaField

__author__ = 'Martin'

def collectorData(cls, view):
    return view.collector.unwrap(sparse = True) if view.collector else {}
def collectorMeta(cls, view):
    collectorId = view.request.matchdict.get('collectorId')
    if collectorId:
        return GetCollectorMetaProc(view.request, collectorId)
    else:
        return {}
def persistCollectorMeta(cls, request, values):
    cls.setCollectorMeta(request, request.matchdict['collectorId'], values)
    return {'success': True, 'message':"Changes saved!"}


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
class CollectorCreateForm(BaseAdminForm):
    id = "basic"
    label = "Basic"
    getFormValues = classmethod(collectorData)
    fields = [
        StringField('firstName', 'First Name', REQUIRED)
        , StringField('lastName', 'Last Name', REQUIRED)
        , StringField('origName', 'Name in orig. Language')
        , ConfigChoiceField('title', 'Title', 'Title', IMPORTANT)
        , DateField('dob', 'Born', IMPORTANT)
        , ConfigChoiceField('gender', 'Gender', 'Gender', IMPORTANT)
        , ConfigChoiceField('nationality', 'Nationality', 'Nationality', IMPORTANT)
        , PictureUploadField('picture', 'Picture', attrs = PictureUploadAttrs())
        , AddressForm('Address', 'Location')
        , UniversityForm('University', classes = 'form-embedded-wrapper form-inline')
        , MultiConfigChoiceField('name', 'Area of interest', "Interest", "Interest")
    ]


    @classmethod
    def persist(cls, request, values):
        try:
            collector = CreateCollectorProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'redirect': request.fwd_url("admin_collector_edit", collectorId = collector.id, stage='basic')}


class CollectorEditForm(CollectorCreateForm):
    id = "basic"
    @classmethod
    def persist(cls, request, values):
        values['University'] = filter(itemgetter("name"), values.get('University', []))
        values['id'] = request.matchdict['collectorId']
        try:
            collector = EditCollectorBaseProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}





class MultiEmailField(MultipleFormField):
    fields = [EmailField('address', 'Email', IMPORTANT, input_classes="input-xlarge")]
class NetworkField(MultipleFormField):
    fields = [ConfigChoiceField('name', None, 'Network', default_none = False), URLField('url', '', attrs = Placeholder("link"))]
class CollectorContactsForm(BaseAdminForm):
    id = "contacts"
    label = "Contacts"
    getFormValues = classmethod(collectorData)
    fields = [
        URLField('wikipedia', 'Wikipedia', IMPORTANT, input_classes="input-xlarge")
        , MultiEmailField('Email', None)
        , PlainHeadingField("Social networks")
        , NetworkField("Network", classes = "form-controls-inline form-inline form-embedded-wrapper")
    ]
    @classmethod
    def persist(cls, request, values):
        values['id'] = request.matchdict['collectorId']
        values['Email'] = filter(itemgetter("address"), values.get('Email', []))
        values['Network'] = filter(itemgetter("url"), values.get('Network', []))
        try:
            collector = EditCollectorContactsProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}



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

class CollectorBusinessForm(BaseAdminForm):
    id = "business"
    label = "Business / Industry"
    getFormValues = classmethod(collectorData)
    fields = [
        CompanyForm("Company")
        , PlainHeadingField('Further industries / type of businesses')
        , MultiConfigChoiceField('name', 'Name', "Industry", "Industry", attrs = REQUIRED)
    ]
    @classmethod
    def persist(cls, request, values):
        values['id'] = request.matchdict['collectorId']
        values['Company'] = filter(itemgetter("name"), values.get('Company', []))
        try:
            collector = EditCollectorBusinessProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}




class CollectionAddCollectorForm(CollectorCreateForm):
    fields = CollectorCreateForm.fields + [HiddenField('collectionId')]



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

class CollectorUploadForm(BaseAdminForm):
    id = "uploads"
    label = "Uploads"
    getFormValues = classmethod(collectorData)
    fields = [
        PlainHeadingField("Collector Documents")
        , TypedFileUploadField("Document", classes = 'form-embedded-wrapper form-inline')
    ]
    @classmethod
    def persist(cls, request, values):
        try:
            values['id'] = request.matchdict['collectorId']
            collector = SaveCollectorDocumentsProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}


class MuseumForm(MultipleFormField):
    fields = [
        ConfigChoiceField("museum", "Top 100 Museum", "TopMuseum")
        , StringField("other_name", "Not Top 100 Museum, then name", label_classes='double')
        , ConfigChoiceField('position', 'Position', 'CollectionPosition')
        , StringField("year", "Year")
        , TokenTypeAheadField('Country', 'Country', '/admin/search/address', 'AddressSearchResult', None, REQUIRED)
        , TokenTypeAheadField('Region', 'Region', '/admin/search/address', 'AddressSearchResult', 'Country')
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Country Region', REQUIRED)
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
    ]

class CollectorArtAdvisoryForm(BaseAdminForm):
    id = "artadvisory"
    label = "Art Engagement"
    getFormValues = classmethod(collectorMeta)
    fields = [
        MuseumForm("Museum")
    ]
    persist = classmethod(persistCollectorMeta)


class OtherFactForm(MultipleFormField):
    fields=[TextareaField('value', "Fact", input_classes="span10")]
class CollectorOtherFactsForm(BaseAdminForm):
    id = "otherfacts"
    label = "Other Facts"
    getFormValues = classmethod(collectorData)
    fields = [
        PlainHeadingField("Other Facts")
        , OtherFactForm("Fact")
    ]
    @classmethod
    def persist(cls, request, values):
        try:
            values['id'] = request.matchdict['collectorId']
            collector = SaveCollectorOtherFactsProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}

