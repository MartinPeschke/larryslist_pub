from jsonclient.backend import DBMessage
from jsonclient.cached import refreshAllCacheds
from larryslist.admin.apps.collector.collections_forms import CollectionCreateForm, CollectionEditForm, CollectionArtistsForm, CollectionWebsiteForm, CollectionUploadForm, CollectionMuseumForm, CollectionCooperationForm, CollectionArtAdvisorForm, ArtworkForm
from larryslist.admin.apps.collector.collector_forms import CollectorContactsForm, CollectorBusinessForm, CollectorEditForm, CollectorCreateForm, CollectionAddCollectorForm, CollectorUploadForm, CollectorArtAdvisoryForm, CollectorOtherFactsForm, CollectorRankingForm, CollectorArtFairForm
from larryslist.admin.apps.collector.models import GetCollectorDetailsProc, SetCollectorStatusProc, SaveArtworkProc
from larryslist.lib.baseviews import GenericErrorMessage, GenericSuccessMessage
from larryslist.lib.formlib.handlers import FormHandler
from pyramid.decorator import reify
from pyramid.renderers import render_to_response, render


def getCollector(self):
    collectorId = self.request.matchdict.get('collectorId')
    if collectorId:
        return GetCollectorDetailsProc(self.request, {'id': collectorId})
    else:
        return None


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



def artwork_handler(context, request):
    return {'form': ArtworkForm}
def save_artwork_handler(context, request):
    data = request.json_body
    artist = data.pop("Artist")
    artwork = data.pop("Artwork")
    artist['Artwork'] = [artwork]
    data['Artist'] = [artist]
    try:
        result = SaveArtworkProc(request, data)
    except DBMessage, e:
        return {'dbMessage': e.message}
    return {'html': render("larryslist:admin/templates/collector/artwork.html", {'artwork':artwork}, request)}

class BaseArtHandler(FormHandler):
    forms = []
    admin_forms = []
    activeForm = None


    @reify
    def collector(self): return getCollector(self)
    @reify
    def collection(self):
        return self.collector.Collection if self.collector else None

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
        result['values'][self.activeForm.id] = self.activeForm.getFormValues(self)
        return result
    def getForms(self): return self.forms
    def isActive(self, form): return self.activeForm.id == form.id

    def GET(self):
        request, context = self.request, self.context
        stage = self.request.matchdict.get('stage')
        collectorId = self.request.matchdict.get('collectorId')
        if not self.activeForm and collectorId and stage:
            self.activeForm = self.schemas.get(stage)
        if not self.activeForm:
            for form in self.forms:
                if form.isEnabled(request, self, context.user):
                    self.activeForm = form
                    break
        if not self.activeForm:
            self.forms[1].getLink(request, self, context.user, True)


        result = super(BaseArtHandler, self).GET()

        result['view'] = self
        return render_to_response(self.activeForm.template, result, request = self.request)

class CollectorHandler(BaseArtHandler):
    forms = [CollectorCreateForm, CollectorEditForm, CollectorContactsForm, CollectorBusinessForm, CollectorArtAdvisoryForm, CollectorOtherFactsForm, CollectorRankingForm, CollectorArtFairForm, CollectorUploadForm]
class CollectionHandler(BaseArtHandler):
    forms = [CollectionCreateForm, CollectionEditForm, CollectionArtistsForm, CollectionWebsiteForm, CollectionMuseumForm, CollectionCooperationForm, CollectionArtAdvisorForm, CollectionUploadForm]







class AddCollectorHandler(BaseArtHandler):
    forms = [CollectionAddCollectorForm, CollectorContactsForm, CollectorBusinessForm, CollectorArtAdvisoryForm, CollectorOtherFactsForm, CollectorRankingForm, CollectorArtFairForm, CollectorUploadForm]
    activeForm = CollectionAddCollectorForm

    collector = None
    @reify
    def othercollector(self): return getCollector(self)


def set_review_status(context, request):
    status = request.params.get("status")
    collectorId = request.matchdict['collectorId']
    collector = GetCollectorDetailsProc(request, {'id': collectorId})

    if status == 'SUBMIT' and collector.canSubmitforReview(context.user):
        SetCollectorStatusProc(request, {'id': collectorId, 'status':"SUBMITTED"})
        request.session.flash(GenericSuccessMessage("This collector has now been submitted for review!"), "generic_messages")
    elif status == 'APPROVE' and collector.canReview(context.user):
        SetCollectorStatusProc(request, {'id': collectorId, 'status':"REVIEWED"})
        request.session.flash(GenericSuccessMessage("This collector has now been approved!"), "generic_messages")
    else:
        request.session.flash(GenericErrorMessage("Not allowed"), "generic_messages")
    refreshAllCacheds(request)
    return request.fwd_raw(request.referer)