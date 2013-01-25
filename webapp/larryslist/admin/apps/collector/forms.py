from operator import itemgetter
from jsonclient.backend import DBException
from larryslist.admin.apps.collector.models import CreateCollectorProc, EditCollectorBaseProc, EditCollectorContactsProc, EditCollectorBusinessProc
from larryslist.lib.formlib.formfields import REQUIRED, StringField, BaseForm, ChoiceField, configattr, ConfigChoiceField, DateField, MultipleFormField, IMPORTANT, TypeAheadField, EmailField, HeadingField, URLField, PlainHeadingField, StaticHiddenField

__author__ = 'Martin'

class CollectorBaseForm(BaseForm):
    classes = "form-horizontal form-validated"
    fields = []
    @classmethod
    def toFormData(cls, values):
        return values

class EmbeddedForm(object):
    classes = "well"
    fields = []


class AddressForm(MultipleFormField):
    fields = [
        TypeAheadField('Country', 'Country', '/admin/search/address', None, REQUIRED)
        , TypeAheadField('Region', 'Region', '/admin/search/address', 'Country', REQUIRED)
        , TypeAheadField('City', 'City', '/admin/search/address', 'Region', REQUIRED)
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

def MultiConfigChoiceField(name, label, configKey, *args, **kwargs):
    class cls(MultipleFormField):
        fields = [
            ConfigChoiceField(name, label, configKey)
        ]
    return cls(*args, **kwargs)


class CollectorCreateForm(CollectorBaseForm):
    id = "create"
    label = "Basic"

    fields = [
        StringField('firstName', 'First Name', REQUIRED)
        , StringField('lastName', 'Last Name', REQUIRED)
        , StringField('origName', 'Name in orig. Language')
        , ConfigChoiceField('title', 'Title', 'Title', IMPORTANT)
        , DateField('dob', 'Born', IMPORTANT)
        , ConfigChoiceField('gender', 'Gender', 'Gender', IMPORTANT)
        , ConfigChoiceField('nationality', 'Nationality', 'Nationality', IMPORTANT)
        , AddressForm('Address', 'Location', REQUIRED)
        , UniversityForm('University', attrs = REQUIRED, classes = 'form-embedded-wrapper form-inline')
        , MultiConfigChoiceField('name', 'Area of interest', "Interest", "Interest", attrs = REQUIRED)
    ]

    @classmethod
    def on_success(cls, request, values):
        values['University'] = filter(itemgetter("name"), values.get('University', []))
        try:
            collector = CreateCollectorProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'redirect': request.fwd_url("admin_collector_edit", collectorId = collector.id, workflow='personal', stage='basic')}


class CollectorEditForm(CollectorCreateForm):
    id = "basic"
    @classmethod
    def on_success(cls, request, values):
        values['University'] = filter(itemgetter("name"), values['University'])
        values['id'] = request.matchdict['collectorId']
        try:
            collector = EditCollectorBaseProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}



class MultiEmailField(MultipleFormField):
    fields = [EmailField('address', 'Email', IMPORTANT)]

class NetworkField(MultipleFormField):
    fields = [
        ConfigChoiceField('name', "Network", 'Network'), URLField('url', '')
    ]


class CollectorContactsForm(CollectorBaseForm):
    id = "contacts"
    label = "Contacts"
    fields = [
        HeadingField('{view.collectorName}')
        , MultiEmailField('Email', None, REQUIRED)
        , PlainHeadingField("Social networks")
        , NetworkField("Network", classes = 'form-embedded-wrapper form-inline', attrs = REQUIRED)
        , StringField('wikipedia', 'Wikipedia', IMPORTANT)
    ]
    @classmethod
    def on_success(cls, request, values):
        values['id'] = request.matchdict['collectorId']
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
        StringField("name", "Namke of company")
        , ConfigChoiceField("position", "Position", "Position")
        , ConfigChoiceField("industry", "Industry", "Industry")
        , URLField("url", "Link")
        , PlainHeadingField("Location", tag="span", classes = "heading-absolute")
        , TypeAheadField('Country', 'Country', '/admin/search/address', None)
        , TypeAheadField('Region', 'Region', '/admin/search/address', 'Country')
        , TypeAheadField('City', 'City', '/admin/search/address', 'Region')
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
    ]

class CollectorBusinessForm(CollectorBaseForm):
    id = "business"
    label = "Business / Industry"
    fields = [
        HeadingField('{view.collectorName}')
        , CompanyForm("Company")
        , PlainHeadingField('', tag='hr')
        , MultiConfigChoiceField('name', 'Further industries / type of businesses', "Industry", "Industry", attrs = REQUIRED)
    ]
    @classmethod
    def on_success(cls, request, values):
        values['id'] = request.matchdict['collectorId']
        try:
            collector = EditCollectorBusinessProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}