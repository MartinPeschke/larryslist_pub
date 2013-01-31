from operator import itemgetter
from jsonclient.backend import DBException
from larryslist.admin.apps.collector.models import CreateCollectorProc, EditCollectorBaseProc, EditCollectorContactsProc, EditCollectorBusinessProc, SaveCollectionDocumentsProc, SaveCollectorDocumentsProc
from larryslist.admin.apps.collector.sources_form import SingleSourceForm, BaseAdminForm
from larryslist.lib.formlib.formfields import REQUIRED, StringField, BaseForm, ChoiceField, configattr, ConfigChoiceField, DateField, MultipleFormField, IMPORTANT, TypeAheadField, EmailField, HeadingField, URLField, PlainHeadingField, StaticHiddenField, MultiConfigChoiceField, TokenTypeAheadField, HiddenField, Placeholder, PictureUploadField, PictureUploadAttrs

__author__ = 'Martin'




class AddressForm(MultipleFormField):
    fields = [
        TokenTypeAheadField('Country', 'Country', '/admin/search/address', 'AddressSearchResult', None, REQUIRED)
        , TokenTypeAheadField('Region', 'Region', '/admin/search/address', 'AddressSearchResult', 'Country', REQUIRED)
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Region', REQUIRED)
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
        , TokenTypeAheadField('City', 'City', '/admin/search/address', 'AddressSearchResult', 'Region')
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
    ]

class CollectorBusinessForm(BaseAdminForm):
    id = "business"
    label = "Business / Industry"
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


class DocumentForm(MultipleFormField):
    fields = [
        ConfigChoiceField("type", "Type", "DocumentType")
        , PictureUploadField('file', 'Document', attrs = PictureUploadAttrs())
        , StringField("name", "Name")
    ]
class DocumentUploadForm(BaseAdminForm):
    id = "uploads"
    fields = [
        PlainHeadingField("Collector Documents")
        , DocumentForm("CollectorDocuments", classes = 'form-embedded-wrapper form-inline')
        , PlainHeadingField("Collection Documents")
        , DocumentForm("CollectionDocuments", classes = 'form-embedded-wrapper form-inline')
        , HiddenField("collectionId")
    ]
    @classmethod
    def persist(cls, request, values):

        docs = filter(itemgetter('type'), values.get('CollectorDocuments', []))
        if docs:
            try:
                data = {'Documents':values.get('CollectorDocuments', [])}
                data['id'] = request.matchdict['collectorId']
                collector = SaveCollectorDocumentsProc(request, {'Collector':data})
            except DBException, e:
                return {'success':False, 'message': e.message}

        docs = filter(itemgetter('type'), values.get('CollectionDocuments', []))
        if docs:
            try:
                collection = values['Collection']
                collection['Documents'] = values.get('CollectionDocuments', [])
                data = {'id': request.matchdict['collectorId'], 'Collection': collection}
                collector = SaveCollectionDocumentsProc(request, {'Collector':data})
                pass
            except DBException, e:
                return {'success':False, 'message': e.message}

        return {'success': True, 'message':"Changes saved!"}