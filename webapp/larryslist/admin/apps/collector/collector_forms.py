from operator import itemgetter
from jsonclient.backend import DBException
from larryslist.admin.apps.collector.models import CreateCollectorProc, EditCollectorBaseProc, EditCollectorContactsProc, EditCollectorBusinessProc
from larryslist.lib.formlib.formfields import REQUIRED, StringField, BaseForm, ChoiceField, configattr, ConfigChoiceField, DateField, MultipleFormField, IMPORTANT, TypeAheadField, EmailField, HeadingField, URLField, PlainHeadingField, StaticHiddenField, MultiConfigChoiceField, TokenTypeAheadField

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




class CollectorCreateForm(BaseForm):
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
        , AddressForm('Address', 'Location')
        , UniversityForm('University', classes = 'form-embedded-wrapper form-inline')
        , MultiConfigChoiceField('name', 'Area of interest', "Interest", "Interest")
    ]

    @classmethod
    def on_success(cls, request, values):
        values['University'] = filter(itemgetter("name"), values.get('University', []))
        try:
            collector = CreateCollectorProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'redirect': request.fwd_url("admin_collector_edit", collectorId = collector.id, stage='basic')}


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


class CollectorContactsForm(BaseForm):
    id = "contacts"
    label = "Contacts"
    fields = [
        HeadingField('{view.collectorName}')
        , MultiEmailField('Email', None)
        , PlainHeadingField("Social networks")
        , NetworkField("Network", classes = 'form-embedded-wrapper form-inline')
        , StringField('wikipedia', 'Wikipedia', IMPORTANT)
    ]
    @classmethod
    def on_success(cls, request, values):
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

class CollectorBusinessForm(BaseForm):
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
        values['Company'] = filter(itemgetter("name"), values.get('Company', []))
        try:
            collector = EditCollectorBusinessProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}