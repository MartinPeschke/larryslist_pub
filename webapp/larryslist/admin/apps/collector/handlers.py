from collections import namedtuple
from jsonclient.backend import DBException, DBMessage
import formencode
from larryslist.admin.apps.collector.collections_forms import BaseCollectionForm, CollectionEditForm, CollectionArtistsForm, CollectionWebsiteForm
from larryslist.admin.apps.collector.collector_forms import CollectorContactsForm, CollectorBusinessForm, CollectorEditForm, CollectorCreateForm, CollectionAddCollectorForm, DocumentUploadForm
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




class BaseArtHandler(FormHandler):
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

    def isFormEnabled(self, form): return self.forms[0].id == form.id
    def getForms(self): return self.forms
    def getActiveForm(self):
        stage = self.request.matchdict.get('stage', 'basic')
        return self.schemas.get(stage)
    def isFormActive(self, form):
        return self.getActiveForm().id == form.id

class CollectorCreate(BaseArtHandler):
    forms = [CollectorCreateForm, CollectorContactsForm, CollectorBusinessForm]
    def getFormLink(self, stage = 'basic'): return self.getCollectorLink(stage)
class CollectorEdit(BaseArtHandler):
    forms = [CollectorEditForm, CollectorContactsForm, CollectorBusinessForm]
    def pre_fill_values(self, request, result):
        value, form = self.collector.unwrap(sparse = True), self.getActiveForm()
        result['values'][form.id] = form.toFormData(value)
        return result
    def isFormEnabled(self, form): return True
    def getFormLink(self, stage = 'basic'): return self.getCollectorLink(stage)




class CollectionCreate(BaseArtHandler):
    forms = [BaseCollectionForm, CollectionArtistsForm, CollectionWebsiteForm]
    def getFormLink(self, stage = 'basic'): return self.getCollectionLink(stage)
class CollectionEdit(BaseArtHandler):
    forms = [CollectionEditForm, CollectionArtistsForm, CollectionWebsiteForm]
    def pre_fill_values(self, request, result):
        value, form = self.collector.Collection.unwrap(sparse = True), self.getActiveForm()
        result['values'][form.id] = form.toFormData(value)
        return result
    def isFormEnabled(self, form): return True
    def getFormLink(self, stage = 'basic'): return self.getCollectionLink(stage)



class AddCollectorHandler(BaseArtHandler):
    forms = [CollectionAddCollectorForm, CollectorContactsForm, CollectorBusinessForm]
    def pre_fill_values(self, request, result):
        form = self.getActiveForm()
        result['values'][form.id] = {'collectionId': self.othercollector.Collection.id}
        return result
    def getActiveForm(self): return self.forms[0]
    def getFormLink(self, stage = 'basic'): return self.getCollectionLink(stage)

    @reify
    def collector(self): return None
    @reify
    def othercollector(self):
        return super(AddCollectorHandler, self).collector
    def getSourcesForm(self):
        if self.othercollector:
            return AddSourcesForm(), self.othercollector.unwrap(sparse = True), {}
        else:
            return None, None, None



class DocumentUpload(BaseArtHandler):
    forms = [DocumentUploadForm]
    def getActiveForm(self):
        return self.forms[0]
    def pre_fill_values(self, request, result):
        value, form = self.collector.unwrap(sparse = True), self.getActiveForm()
        result['values'][form.id] = form.toFormData(value)
        result['values'][form.id]['collectionId'] = self.collector.Collection.id
        return result