from collections import namedtuple
from larryslist.admin.apps.collector.collections_forms import BaseCollectionForm, CollectionEditForm
from larryslist.admin.apps.collector.forms import CollectorContactsForm, CollectorBusinessForm, CollectorEditForm, CollectorCreateForm
from larryslist.admin.apps.collector.models import GetCollectorDetailsProc
from larryslist.lib.formlib.handlers import FormHandler
from pyramid.decorator import reify




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
        return '{0.firstName} {0.lastName}'.format(self.collector)

    def getCollectionBaseLink(self):
        if self.collector.Collection:
            return ("admin")

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

class CreateHandler(BaseCollectorHandler):
    forms = [CollectorCreateForm]
    def getActiveForm(self): return self.forms[0]
    def getForms(self): return self.forms
    def isFormEnabled(self, form): return self.forms[0].id == form.id

class EditHandler(CreateHandler):
    forms = [CollectorEditForm, CollectorContactsForm, CollectorBusinessForm]
    def pre_fill_values(self, request, result):
        value = self.collector.unwrap(sparse = True)
        result['values'] = {form.id: form.toFormData(value) for form in self.forms}
        return result
    def getActiveForm(self):
        stage = self.request.matchdict.get('stage', 'basic')
        return self.schemas.get(stage)
    def isFormEnabled(self, form): return True

class CollectionCreate(CreateHandler):
    forms = [BaseCollectionForm]

class CollectionEdit(CreateHandler):
    forms = [CollectionEditForm]
    def pre_fill_values(self, request, result):
        value = self.collector.Collection.unwrap(sparse = True)
        result['values'] = {form.id: form.toFormData(value) for form in self.forms}
        return result
    def getActiveForm(self):
        stage = self.request.matchdict.get('stage', 'basic')
        return self.schemas.get(stage)
    def isFormEnabled(self, form): return True