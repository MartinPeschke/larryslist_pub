from collections import namedtuple
from jsonclient.backend import DBException, DBMessage
import formencode
from larryslist.admin.apps.collector.collections_forms import BaseCollectionForm, CollectionEditForm, CollectionArtistsForm, CollectionWebsiteForm
from larryslist.admin.apps.collector.collector_forms import CollectorContactsForm, CollectorBusinessForm, CollectorEditForm, CollectorCreateForm, CollectionAddCollectorForm
from larryslist.admin.apps.collector.models import GetCollectorDetailsProc, SetSourcesProc, CollectorModel
from larryslist.admin.apps.collector.sources_form import AddSourcesForm
from larryslist.lib.formlib.handlers import FormHandler
from pyramid.decorator import reify

def sources_save(context, request):
    values = formencode.variabledecode.variable_decode(request.json_body)
    data = values['sources']
    data['id'] = request.matchdict['collectorId']
    try:
        collection = SetSourcesProc(request, {'Collector':data})
    except (DBException, DBMessage), e:
        return {'success':False, 'message': e.message}
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
        return self.collector.getName()

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
            return AddSourcesForm(), self.collector.unwrap(sparse = True), {}
        else:
            return None, None, None


class CreateCollectorHandler(BaseCollectorHandler):
    forms = [CollectorCreateForm, CollectorContactsForm, CollectorBusinessForm]
    def isFormActive(self, form): return self.forms[0].id == form.id
    def getForms(self): return self.forms
    def isFormEnabled(self, form): return self.forms[0].id == form.id

class EditHandler(CreateCollectorHandler):
    forms = [CollectorEditForm, CollectorContactsForm, CollectorBusinessForm]
    def pre_fill_values(self, request, result):
        value = self.collector.unwrap(sparse = True)
        result['values'] = {form.id: form.toFormData(value) for form in self.forms}
        return result
    def isFormActive(self, form):
        stage = self.request.matchdict.get('stage', 'basic')
        return self.schemas.get(stage).id == form.id
    def isFormEnabled(self, form): return True

class CollectionCreate(CreateCollectorHandler):
    forms = [BaseCollectionForm, CollectionArtistsForm, CollectionWebsiteForm]

class CollectionEdit(CreateCollectorHandler):
    forms = [CollectionEditForm, CollectionArtistsForm, CollectionWebsiteForm]
    def pre_fill_values(self, request, result):
        value = self.collector.Collection.unwrap(sparse = True)
        result['values'] = {form.id: form.toFormData(value) for form in self.forms}
        return result
    def isFormActive(self, form):
        stage = self.request.matchdict.get('stage', 'basic')
        return self.schemas.get(stage).id == form.id
    def isFormEnabled(self, form): return True


class AddCollectorHandler(CreateCollectorHandler):
    forms = [CollectionAddCollectorForm, CollectorContactsForm, CollectorBusinessForm]
    @reify
    def collector(self):
        return None

    def pre_fill_values(self, request, result):
        result['values'] = {form.id:{'collectionId': self.othercollector.Collection.id} for form in self.forms}
        return result

    @reify
    def othercollector(self):
        return super(AddCollectorHandler, self).collector
    def getSourcesForm(self):
        if self.othercollector:
            return AddSourcesForm(), self.othercollector.unwrap(sparse = True), {}
        else:
            return None, None, None
