from jsonclient.backend import DBException
from larryslist.admin.apps.collector.models import CreateCollectorProc
from larryslist.lib.formlib.formfields import REQUIRED, StringField, BaseForm, ChoiceField, configattr, ConfigChoiceField, DateField, MultipleFormField, IMPORTANT

__author__ = 'Martin'

class CollectorBaseForm(BaseForm):
    classes = "form-horizontal form-validated"
    fields = []

class EmbeddedForm(object):
    classes = "well"
    fields = []


class AddressForm(MultipleFormField):
    fields = [
        StringField('Country', 'Country', REQUIRED)
        , StringField('Region', 'Region', REQUIRED)
        , StringField('City', 'City', REQUIRED)
        , StringField('postCode', 'Post Code')
        , StringField('line1', 'Street 1')
        , StringField('line2', 'Street 2')
        , StringField('line3', 'Street 3')
    ]





class CollectorBaseForm(CollectorBaseForm):
    id = "collector_base"
    label = "Basic"

    fields = [
        StringField('firstName', 'First Name', REQUIRED)
        , StringField('lastName', 'Last Name', REQUIRED)
        , StringField('originalName', 'Name in orig. Language')
        , ConfigChoiceField('Title', IMPORTANT)
        , DateField('dob', 'Born', IMPORTANT)
        , ConfigChoiceField('Gender', IMPORTANT)
        , ConfigChoiceField('Nationality', IMPORTANT)
        , AddressForm('address', 'Location', REQUIRED)
    ]

    @classmethod
    def on_success(cls, request, values):
        try:
            result = CreateCollectorProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {}


class CollectorContactsForm(CollectorBaseForm):
    id = "collector_contacts"
    label = "Contacts"

class CollectorBusinessForm(CollectorBaseForm):
    id = "collector_business"
    label = "Business / Industry"