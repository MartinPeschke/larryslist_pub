from larryslist.lib.formlib.formfields import REQUIRED, StringField, BaseForm, ChoiceField, configattr, ConfigChoiceField, DateField

__author__ = 'Martin'

class CollectorBaseForm(BaseForm):
    classes = "form-horizontal form-validated"
    fields = []

class CollectorBaseForm(CollectorBaseForm):
    id = "collector_base"
    label = "Basic"

    fields = [
        StringField('firstName', 'First Name', REQUIRED)
        , StringField('lastName', 'Last Name', REQUIRED)
        , StringField('originalName', 'Name in orig. Language')
        , ConfigChoiceField('Title')
        , DateField('dob', 'Born', REQUIRED)
        , ConfigChoiceField('Gender')
        , ConfigChoiceField('Nationality')
    ]

    @classmethod
    def on_success(cls, request, values):
        return {}


class CollectorContactsForm(CollectorBaseForm):
    id = "collector_contacts"
    label = "Contacts"

class CollectorBusinessForm(CollectorBaseForm):
    id = "collector_business"
    label = "Business / Industry"