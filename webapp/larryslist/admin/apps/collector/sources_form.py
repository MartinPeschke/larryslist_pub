from operator import itemgetter
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
    classes = "form-controls-inline form-inline"
    fields = [
        SingleSourceForm('Source', None)
    ]

class BaseAdminForm(BaseForm):
    extra_forms = [AddSourcesForm]

    @classmethod
    def clean_data(cls, request, values):
        if 'University' in values:
            values['University'] = filter(itemgetter("name"), values.get('University', []))
        if 'sources' in values:
            values['sources'] = filter(itemgetter("type"), values.get('Source', []))
        if 'collectionId' in values:
            v = values.setdefault('Collection', {})
            v['id']  = values.pop('collectionId')
        return values

    @classmethod
    def on_success(cls, request, values):
        cls.clean_data(request, values)
        extra_forms = {}
        for f in cls.extra_forms:
            extra_forms[f.id] = values.pop(f.id, {})
        result = cls.persist(request, values)

        return result