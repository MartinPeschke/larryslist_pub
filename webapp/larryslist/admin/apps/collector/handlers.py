from collections import namedtuple
from larryslist.admin.apps.collector.forms import CollectorBaseForm, CollectorContactsForm, CollectorBusinessForm
from larryslist.lib.formlib.handlers import FormHandler

__author__ = 'Martin'



class CreateHandler(FormHandler):
    forms = [CollectorBaseForm, CollectorContactsForm, CollectorBusinessForm]

    def getActiveForm(self):
        return CollectorBaseForm

    def getForms(self):
        return self.forms

    def isFormEnabled(self, form):
        request = self.request
        if 'collectorId' in request.matchdict:
            return True
        else:
            return CollectorBaseForm.id == form.id
