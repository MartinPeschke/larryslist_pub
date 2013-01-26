from larryslist.lib.formlib.formfields import BaseForm, ConfigChoiceField, StringField


class AddSourcesForm(BaseForm):
    id='sources'
    label = 'Sources'
    classes = "form-horizontal form-validated form-inline"
    fields = [
        ConfigChoiceField('type', 'Type of source', 'SourceType')
        , StringField('name', '')
        , StringField('location', '')
        , StringField('year', '')
    ]

