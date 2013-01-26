from jsonclient.backend import DBException
from larryslist.admin.apps.collector.models import SetSourcesProc
from larryslist.lib.formlib.formfields import BaseForm, ConfigChoiceField, StringField, MultipleFormField


class SingleSourceForm(MultipleFormField):
    fields = [
        ConfigChoiceField('type', 'Type of source', 'SourceType')
        , StringField('title', 'Title')
        , StringField('author', 'Author', input_classes="input-medium")
        , StringField('year', 'Year', input_classes="input-mini digits")
    ]

class AddSourcesForm(BaseForm):
    id='sources'
    label = 'Sources'
    classes = "form-horizontal form-validated form-inline"
    fields = [
        SingleSourceForm('Source', None, classes="form-inline")
    ]