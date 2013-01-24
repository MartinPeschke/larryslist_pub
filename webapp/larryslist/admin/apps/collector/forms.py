from operator import itemgetter
from jsonclient.backend import DBException
from larryslist.admin.apps.collector.models import CreateCollectorProc, EditCollectorBaseProc, EditCollectorContactsProc
from larryslist.lib.formlib.formfields import REQUIRED, StringField, BaseForm, ChoiceField, configattr, ConfigChoiceField, DateField, MultipleFormField, IMPORTANT, TypeAheadField, EmailField, HeadingField

__author__ = 'Martin'

class CollectorBaseForm(BaseForm):
    classes = "form-horizontal form-validated"
    fields = []

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
    classes = 'form-inline'
    fields = [
        StringField('name', 'Name of University')
        , StringField('city', 'City')
        ]

class MultiConfigChoiceField(MultipleFormField):
    fields = [
        ConfigChoiceField('name', 'Area of interest', "Interest")
    ]


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
        , UniversityForm('University')
        , MultiConfigChoiceField("Interest")
    ]

    @classmethod
    def on_success(cls, request, values):
        values['University'] = filter(itemgetter("name"), values.get('University', []))
        values['Interest'] = [{'name':n} for n in values.get('Interest',[])]
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


class CollectorContactsForm(CollectorBaseForm):
    id = "contacts"
    label = "Contacts"
    fields = [
        HeadingField("{firstName} {lastName}")
        , MultiEmailField('Email', None, IMPORTANT)
    ]
    @classmethod
    def on_success(cls, request, values):
        values['id'] = request.matchdict['collectorId']
        try:
            collector = EditCollectorContactsProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'message':"Changes saved!"}

class CollectorBusinessForm(CollectorBaseForm):
    id = "business"
    label = "Business / Industry"