from operator import itemgetter
from jsonclient.backend import DBException
from larryslist.admin.apps.collector.collector_forms_fields import collectorCreateFields, collectorContactsFields, collectorBusinessFields, collectionAddCollectorForm, collectorUploadFields, collectorArtAdvisoryFields, collectorOtherFactsFields, collectorRankingFields, collectorArtFairFields
from larryslist.admin.apps.collector.models import CreateCollectorProc, EditCollectorBaseProc, EditCollectorContactsProc, EditCollectorBusinessProc, SaveCollectorDocumentsProc, SaveCollectorOtherFactsProc, SetCollectorMetaProc
from larryslist.admin.apps.collector.sources_form import BaseAdminForm
from larryslist.models.collector import GetCollectorMetaProc


def collectorData(cls, view):
    return view.collector.unwrap(sparse = True) if view.collector else {}
def collectorMeta(cls, view):
    collectorId = view.request.matchdict.get('collectorId')
    if collectorId:
        return GetCollectorMetaProc(view.request, collectorId)
    else:
        return {}
def getCombinedData(cls, view):
    result = collectorMeta(cls, view)
    result.update(collectorData(cls, view))
    return result


def persistCollectorMeta(cls, request, values):
    data = {}
    collectorId = request.matchdict.get('collectorId')
    if collectorId:
        data = GetCollectorMetaProc(request, collectorId)
    data.update(values)
    SetCollectorMetaProc(request, collectorId, data)
    return {'success': True}

def always(cls, request, view, user): return True
def onlyAdmin(cls, request, view, user): return user.isAdmin()
def isAllowedCreateForm(cls, request, view, user):
    return view.collector is None
def isAllowedEditForm(cls, request, view, user):
    return view.collector is not None
def isAllowedAdminForm(cls, request, view, user):
    return user.isAdmin() and view.collector is not None

def getCreateLink(cls, request, view, user, forward = False):
    f = request.fwd if forward else request.fwd_url
    return f("admin_collector_create")

def getEditLink(cls, request, view, user, forward = False):
    f = request.fwd if forward else request.fwd_url
    return f("admin_collector_edit", collectorId = view.collector.id, stage = cls.id)

class CollectorCreateForm(BaseAdminForm):
    id = "basecreate"
    label = "Basic"

    getFormValues = classmethod(collectorData)
    isShown = classmethod(isAllowedCreateForm)
    isEnabled = classmethod(isAllowedCreateForm)
    getLink = classmethod(getCreateLink)

    fields = collectorCreateFields
    @classmethod
    def persist(cls, request, values):
        try:
            values['feederToken'] = request.root.user.token
            collector = CreateCollectorProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'redirect': request.fwd_url("admin_collector_edit", collectorId = collector.id, stage='basic'), 'collectorId': collector.id}

class CollectorEditForm(BaseAdminForm):
    id = "base"
    label = "Basic"

    getFormValues = classmethod(collectorData)
    isShown = classmethod(isAllowedEditForm)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectorCreateFields
    @classmethod
    def persist(cls, request, values):
        values['University'] = filter(itemgetter("name"), values.get('University', []))
        values['id'] = request.matchdict['collectorId']
        try:
            collector = EditCollectorBaseProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True}

class CollectorContactsForm(BaseAdminForm):
    id = "contacts"
    label = "Contacts"

    getFormValues = classmethod(collectorData)
    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectorContactsFields
    @classmethod
    def persist(cls, request, values):
        values['id'] = request.matchdict['collectorId']
        values['Email'] = filter(itemgetter("address"), values.get('Email', []))
        values['Network'] = filter(itemgetter("url"), values.get('Network', []))
        try:
            collector = EditCollectorContactsProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True}

class CollectorBusinessForm(BaseAdminForm):
    id = "business"
    label = "Business / Industry"

    getFormValues = classmethod(collectorData)
    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectorBusinessFields
    @classmethod
    def persist(cls, request, values):
        values['id'] = request.matchdict['collectorId']
        values['Company'] = filter(itemgetter("name"), values.get('Company', []))
        try:
            collector = EditCollectorBusinessProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True}

class CollectorUploadForm(BaseAdminForm):
    id = "uploads"
    label = "Uploads"

    getFormValues = classmethod(getCombinedData)
    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectorUploadFields
    @classmethod
    def persist(cls, request, values):
        atts = values.pop('Attachments', None)
        if atts is not None:
            persistCollectorMeta(CollectorUploadForm, request, {'Attachments': atts})

        try:
            values['id'] = request.matchdict['collectorId']
            collector = SaveCollectorDocumentsProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True}

class CollectorArtAdvisoryForm(BaseAdminForm):
    id = "artadvisory"
    label = "Art Engagement"
    requires_config = True

    getFormValues = classmethod(collectorMeta)
    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectorArtAdvisoryFields
    persist = classmethod(persistCollectorMeta)

class CollectorOtherFactsForm(BaseAdminForm):
    id = "otherfacts"
    label = "Other Facts"

    getFormValues = classmethod(collectorData)
    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectorOtherFactsFields
    @classmethod
    def persist(cls, request, values):
        try:
            values['id'] = request.matchdict['collectorId']
            collector = SaveCollectorOtherFactsProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True}


class CollectorRankingForm(BaseAdminForm):
    id = "ranking"
    label = "Rankings"

    getFormValues = classmethod(collectorMeta)
    isShown = classmethod(onlyAdmin)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectorRankingFields
    @classmethod
    def persist(cls, request, values):
        unique = set()
        result = []
        keyGet = itemgetter('name', 'year')
        for map in sorted(values.get('Ranking', []), key=keyGet):
            if keyGet(map) not in unique:
                unique.add(keyGet(map))
                result.append(map)
        values['Ranking'] = result
        return persistCollectorMeta(cls, request, values)

class CollectorArtFairForm(BaseAdminForm):
    id = "artfair"
    label = "Art Fairs"

    getFormValues = classmethod(collectorMeta)
    isShown = classmethod(onlyAdmin)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectorArtFairFields
    @classmethod
    def persist(cls, request, values):
        unique = set()
        result = []
        keyGet = itemgetter('name', 'year')
        for map in sorted(values.get('ArtFair', []), key=keyGet):
            if keyGet(map) not in unique:
                unique.add(keyGet(map))
                result.append(map)
        values['ArtFair'] = result
        return persistCollectorMeta(cls, request, values)







class CollectionAddCollectorForm(BaseAdminForm):
    id = "base"
    label = "Basic"
    template = "larryslist:admin/templates/collector/collectoradd.html"

    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    @classmethod
    def getLink(cls, request, view, user, forward = False):
        f = request.fwd if forward else request.fwd_url
        return f("admin_collector_add_collector", collectorId = view.othercollector.id)
    fields = collectionAddCollectorForm
    @classmethod
    def getFormValues(cls, view):
        return {'collectionId': view.othercollector.Collection.id}
    @classmethod
    def persist(cls, request, values):
        try:
            values['feederToken'] = request.root.user.token
            values['LinkedCollector'] = {'id': request.matchdict['collectorId'], 'relation':values.pop("relation")}
            collector = CreateCollectorProc(request, {'Collector':values})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'redirect': request.fwd_url("admin_collector_edit", collectorId = collector.id, stage='basic')}
