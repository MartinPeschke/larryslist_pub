from operator import itemgetter
from jsonclient.backend import DBException
from larryslist.admin.apps.collector.models import SetSourcesProc, GetCollectorMetaProc, SetCollectorMetaProc, SetCollectionMetaProc, GetCollectionMetaProc
from larryslist.lib.formlib.formfields import BaseForm, ConfigChoiceField, StringField, MultipleFormField, Placeholder, DependentAttrs


class SingleSourceForm(MultipleFormField):
    fields = [
        ConfigChoiceField('type', None, 'SourceType', attrs = Placeholder('Source type'))

        , StringField('url', None, input_classes='input-xxlarge', attrs = DependentAttrs('Internet / Blog / Online Mag url', dependency='type', dependencyValue= 'Internet/Blogs/Online Mag'))

        , StringField('title', None, attrs = DependentAttrs('Book title/Newspaper name', dependency='type', dependencyValue= 'Book Magazine Newspaper'))
        , StringField('publisher', None, attrs = DependentAttrs('Publisher', dependency='type', dependencyValue= 'Book'))
        , StringField('author', None, attrs = DependentAttrs('Author', dependency='type', dependencyValue= 'Book'))
        , StringField('year', None, input_classes="input-mini", attrs = DependentAttrs('Year published', dependency='type', dependencyValue= 'Book'))

        , StringField('name', None, attrs = DependentAttrs('Article title', dependency='type', dependencyValue= 'Newspaper Magazine'))
        , StringField('date', None, attrs = DependentAttrs('Date / Volume', dependency='type', dependencyValue= 'Newspaper Magazine'))
    ]

class AddSourcesForm(BaseForm):
    id='sources'
    label = 'Sources'
    classes = "form-controls-inline form-inline"
    fields = [
        SingleSourceForm('Source', None)
    ]

class BaseAdminForm(BaseForm):
    template = "larryslist:admin/templates/collector/form.html"
    extra_forms = [AddSourcesForm]
    fields = []

    @classmethod
    def clean_data(cls, request, values):
        if 'University' in values:
            values['University'] = filter(itemgetter("name"), values.get('University', []))
        if 'sources' in values:
            values['sources'] = filter(itemgetter("type"), values['sources'].get('Source', []))
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
        if result.get('success'):
            sources = extra_forms[AddSourcesForm.id]
            if sources:
                sources = {'id': request.matchdict['collectorId'], 'Source': sources}
                try:
                    collection = SetSourcesProc(request, {'Collector':sources})
                except DBException, e:
                    return {'success':False, 'message': e.message}
                return {'success': True}
        return result