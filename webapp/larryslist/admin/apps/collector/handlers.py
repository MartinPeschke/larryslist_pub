from collections import namedtuple
from larryslist.admin.apps.collector.collections_forms import BaseCollectionForm, CollectionEditForm, CollectionArtistsForm, CollectionWebsiteForm
from larryslist.admin.apps.collector.collector_forms import CollectorContactsForm, CollectorBusinessForm, CollectorEditForm, CollectorCreateForm
from larryslist.admin.apps.collector.models import GetCollectorDetailsProc
from larryslist.admin.apps.collector.sources_form import AddSourcesForm
from larryslist.lib.formlib.handlers import FormHandler
from pyramid.decorator import reify

def sources_save(context, request):

    return {'success': True, 'message':"Changes saved!"}




class BaseCollectorHandler(FormHandler):
    @reify
    def collector(self):
        collectorId = self.request.matchdict.get('collectorId')
        if collectorId:
            return GetCollectorDetailsProc(self.request, {'id': collectorId})
        else:
            return None
    @reify
    def collectorName(self):
        return u'{0.firstName} {0.lastName}'.format(self.collector)

    def getCollectorLink(self, stage = 'basic'):
        req = self.request
        if self.collector:
            return req.fwd_url("admin_collector_edit", collectorId = self.collector.id, stage=stage)
        else:
            return req.fwd_url("admin_collector_create")

    def getCollectionLink(self, stage = 'basic'):
        req = self.request
        if not self.collector:
            return None
        elif self.collector.Collection:
            return req.fwd_url("admin_collection_edit", collectorId = self.collector.id, stage = stage)
        else:
            return req.fwd_url("admin_collection_create", collectorId = self.collector.id)

    def getSourcesForm(self):
        if self.collector:
            return AddSourcesForm()
        else:
            return None


class CreateHandler(BaseCollectorHandler):
    forms = [CollectorCreateForm]
    def isFormActive(self, form): return self.forms[0].id == form.id
    def getForms(self): return self.forms
    def isFormEnabled(self, form): return self.forms[0].id == form.id

class EditHandler(CreateHandler):
    forms = [CollectorEditForm, CollectorContactsForm, CollectorBusinessForm]
    def pre_fill_values(self, request, result):
        value = self.collector.unwrap(sparse = True)
        result['values'] = {form.id: form.toFormData(value) for form in self.forms}
        return result
    def isFormActive(self, form):
        stage = self.request.matchdict.get('stage', 'basic')
        return self.schemas.get(stage).id == form.id
    def isFormEnabled(self, form): return True

class CollectionCreate(CreateHandler):
    forms = [BaseCollectionForm]

class CollectionEdit(CreateHandler):
    forms = [CollectionEditForm, CollectionArtistsForm, CollectionWebsiteForm]
    def pre_fill_values(self, request, result):
        value = self.collector.Collection.unwrap(sparse = True)
        result['values'] = {form.id: form.toFormData(value) for form in self.forms}
        return result
    def isFormActive(self, form):
        stage = self.request.matchdict.get('stage', 'basic')
        return self.schemas.get(stage).id == form.id
    def isFormEnabled(self, form): return True