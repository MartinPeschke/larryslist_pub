from larryslist.admin.apps.collector.forms import CollectorBaseForm, CollectorContactsForm, CollectorBusinessForm, CollectorEditForm, CollectorCreateForm
from larryslist.admin.apps.collector.models import GetCollectorDetailsProc
from larryslist.lib.formlib.handlers import FormHandler



class CreateHandler(FormHandler):
    forms = [CollectorCreateForm, CollectorEditForm, CollectorContactsForm, CollectorBusinessForm]

    def getActiveForm(self):
        return CollectorBaseForm

    def getForms(self):
        return self.forms

    def isFormEnabled(self, form):
        return CollectorBaseForm.id == form.id


class EditHandler(CreateHandler):
    forms = [CollectorEditForm, CollectorContactsForm, CollectorBusinessForm]

    def add_globals(self, request, result):
        self.collector = GetCollectorDetailsProc(request, {'id': request.matchdict['collectorId']})
        return result
    def pre_fill_values(self, request, result):
        value = self.collector.unwrap(sparse = True)
        result['values'] = {form.id: value for form in self.forms}
        return result

    def getActiveForm(self):
        return self.schemas.get(self.request.matchdict['stage'])

    def isFormEnabled(self, form):
        return True
