from jsonclient.backend import DBException
from larryslist.admin.apps.collector.models import SetSourcesProc
from larryslist.lib.formlib.formfields import BaseForm, ConfigChoiceField, StringField, MultipleFormField, Placeholder


class SingleSourceForm(MultipleFormField):
    fields = [
        ConfigChoiceField('type', None, 'SourceType', attrs = Placeholder('Source type'))
        , StringField('title', None, attrs = Placeholder('Source type'))
        , StringField('author', None, input_classes="input-medium", attrs = Placeholder('Author'))
        , StringField('year', None, input_classes="input-mini digits", attrs = Placeholder('Year'))
    ]

class AddSourcesForm(BaseForm):
    id='sources'
    label = 'Sources'
    classes = "form-validated form-controls-inline form-inline"
    fields = [
        SingleSourceForm('Source', None)
    ]