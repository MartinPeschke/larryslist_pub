from collections import namedtuple
from jsonclient.backend import DBException, DBMessage
import formencode
from larryslist.admin.apps.collector.collections_forms import BaseCollectionForm, CollectionEditForm, CollectionArtistsForm, CollectionWebsiteForm, CollectionUploadForm, CollectionMuseumForm, CollectionCooperationForm, CollectionArtAdvisor
from larryslist.admin.apps.collector.collector_forms import CollectorContactsForm, CollectorBusinessForm, CollectorEditForm, CollectorCreateForm, CollectionAddCollectorForm, CollectorUploadForm, CollectorArtAdvisoryForm, CollectorOtherFactsForm
from larryslist.admin.apps.collector.models import GetCollectorDetailsProc, SetSourcesProc, CollectorModel, GetCollectorMetaProc
from larryslist.admin.apps.collector.sources_form import AddSourcesForm
from larryslist.lib.formlib.handlers import FormHandler
from pyramid.decorator import reify
from pyramid.renderers import render_to_response


def sources_save(context, request):
    values = formencode.variabledecode.variable_decode(request.json_body)
    data = values['sources']
    data['id'] = request.matchdict['collectorId']
    try:
        collection = SetSourcesProc(request, {'Collector':data})
    except (DBException, DBMessage), e:
        return {'success':False, 'message': e.message}
    return {'success': True, 'message':"Changes saved!"}



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


class BaseArtHandler(FormHandler):
    @reify
    def collector(self):
        collectorId = self.request.matchdict.get('collectorId')
        if collectorId:
            return GetCollectorDetailsProc(self.request, {'id': collectorId})
        else:
            return None
    @reify
    def collection(self): return self.collector.Collection

    @reify
    def collectorName(self): return self.collector.getName()
    getCollectorLink = getCollectorLink
    getCollectionLink = getCollectionLink


    def getSourceValues(self):
        if self.collector:
            return self.collector.unwrap(sparse = True), {}
        else:
            return {}, {}
    def pre_fill_values(self, request, result):
        form = self.getActiveForm()
        result['values'][form.id] = form.getFormValues(self)
        return result
    def isFormEnabled(self, form): return self.forms[0].id == form.id
    def getForms(self): return self.forms
    def getActiveForm(self):
        stage = self.request.matchdict.get('stage', 'basic')
        return self.schemas.get(stage)
    def isFormActive(self, form):
        return self.getActiveForm().id == form.id


    def GET(self):
        result = super(BaseArtHandler, self).GET()
        form = self.getActiveForm()
        if hasattr(form, 'template'):
            result['view'] = self
            return render_to_response(form.template, result, request = self.request)
        else:
            return result


class CollectorCreate(BaseArtHandler):
    forms = [CollectorCreateForm, CollectorContactsForm, CollectorBusinessForm, CollectorArtAdvisoryForm, CollectorOtherFactsForm, CollectorUploadForm]
    def getFormLink(self, stage = 'basic'): return self.getCollectorLink(stage)
class CollectorEdit(BaseArtHandler):
    forms = [CollectorEditForm, CollectorContactsForm, CollectorBusinessForm, CollectorArtAdvisoryForm, CollectorOtherFactsForm, CollectorUploadForm]
    getFormLink = getCollectorLink
    def isFormEnabled(self, form): return True





class CollectionCreate(BaseArtHandler):
    forms = [BaseCollectionForm, CollectionArtistsForm, CollectionWebsiteForm, CollectionMuseumForm, CollectionCooperationForm, CollectionArtAdvisor, CollectionUploadForm]
    def getFormLink(self, stage = 'basic'): return self.getCollectionLink(stage)
class CollectionEdit(BaseArtHandler):
    forms = [CollectionEditForm, CollectionArtistsForm, CollectionWebsiteForm, CollectionMuseumForm, CollectionCooperationForm, CollectionArtAdvisor, CollectionUploadForm]
    getFormLink = getCollectionLink
    def isFormEnabled(self, form): return True




class AddCollectorHandler(BaseArtHandler):
    forms = [CollectionAddCollectorForm, CollectorContactsForm, CollectorBusinessForm]
    getFormLink = getCollectionLink
    def getActiveForm(self): return self.forms[0]

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
