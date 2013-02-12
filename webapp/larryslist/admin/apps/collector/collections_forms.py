from jsonclient.backend import DBException
from larryslist.admin.apps.collector.collections_forms_fields import baseCollectionFields, collectionEditFields, collectionArtistsFields, collectionWebsiteFields, collectionUploadFields, collectionMuseumFields, collectionCooperationFields, collectionArtAdvisorFields
from larryslist.admin.apps.collector.models import CreateCollectionProc, EditCollectionBaseProc, EditCollectionArtistsProc, EditCollectionPublicationsProc, SaveCollectionDocumentsProc, GetCollectionMetaProc, SetCollectionMetaProc
from larryslist.admin.apps.collector.sources_form import BaseAdminForm

__author__ = 'Martin'


def collectionData(cls, view):
    return view.collection.unwrap(sparse = True) if view.collection else {}
def collectionMeta(cls, view):
    if view.collection:
        result = GetCollectionMetaProc(view.request, str(view.collection.id))
        result['id'] = view.collection.id
        return result
    else:
        return {}

def getCombinedData(cls, view):
    result = collectionMeta(cls, view)
    result.update(collectionData(cls, view))
    return result

def persistCollectionMeta(cls, request, values):
    id = values['id']
    data = GetCollectionMetaProc(request, id)
    data.update(values)
    SetCollectionMetaProc(request, id, data)
    return {'success': True}

def always(cls, request, view, user): return True
def isAllowedCreateForm(cls, request, view, user):
    return not view.collection
def isAllowedEditForm(cls, request, view, user):
    return bool(view.collection)
def isAllowedAdminForm(cls, request, view, user):
    return user.isAdmin() and view.collection is not None

def getCreateLink(cls, request, view, user, forward = False):
    f = request.fwd if forward else request.fwd_url
    return f("admin_collection_create", collectorId = view.collector.id)

def getEditLink(cls, request, view, user, forward = False):
    f = request.fwd if forward else request.fwd_url
    return f("admin_collection_edit", collectorId = view.collector.id, stage = cls.id)





class CollectionCreateForm(BaseAdminForm):
    id = 'basecreate'
    label = 'Basic'
    getFormValues = classmethod(collectionData)

    isShown = classmethod(isAllowedCreateForm)
    isEnabled = classmethod(isAllowedCreateForm)
    getLink = classmethod(getCreateLink)

    fields = baseCollectionFields
    @classmethod
    def persist(cls, request, values):
        collectorId = request.matchdict['collectorId']
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = CreateCollectionProc(request, values)
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True, 'redirect': request.fwd_url("admin_collection_edit", collectorId = collectorId, stage='basic')}


class CollectionEditForm(CollectionCreateForm):
    id = 'base'
    label = 'Basic'

    getFormValues = classmethod(collectionData)
    isShown = classmethod(isAllowedEditForm)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectionEditFields
    @classmethod
    def persist(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = EditCollectionBaseProc(request, values)
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True}

class CollectionArtistsForm(BaseAdminForm):
    id = 'artist'
    label = 'Artists'

    getFormValues = classmethod(collectionData)
    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectionArtistsFields
    @classmethod
    def persist(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection':values}
        try:
            collection = EditCollectionArtistsProc(request, values)
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True}

class CollectionWebsiteForm(BaseAdminForm):
    id = 'website'
    label = 'Communication Platforms'

    getFormValues = classmethod(collectionData)
    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectionWebsiteFields
    @classmethod
    def persist(cls, request, values):
        values = {'id': request.matchdict['collectorId'], 'Collection': values}
        try:
            collection = EditCollectionPublicationsProc(request, values)
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True}


class CollectionUploadForm(BaseAdminForm):
    id = "uploads"
    label = "Uploads"

    getFormValues = classmethod(getCombinedData)
    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectionUploadFields
    @classmethod
    def persist(cls, request, values):
        atts = values.pop('Attachments', None)
        if atts is not None:
            persistCollectionMeta(CollectionUploadForm, request, {'Attachments': atts, 'id': values.get('id')})

        try:
            data = {'id':request.matchdict['collectorId'], 'Collection': values}
            collector = SaveCollectionDocumentsProc(request, {'Collector':data})
        except DBException, e:
            return {'success':False, 'message': e.message}
        return {'success': True}


class CollectionMuseumForm(BaseAdminForm):
    id = 'museum'
    label = 'Museum'

    getFormValues = classmethod(collectionMeta)
    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectionMuseumFields
    persist = classmethod(persistCollectionMeta)

class CollectionCooperationForm(BaseAdminForm):
    id="cooperation"
    label = "Cooperation"

    getFormValues = classmethod(collectionMeta)
    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectionCooperationFields
    persist = classmethod(persistCollectionMeta)

class CollectionArtAdvisorForm(BaseAdminForm):
    id="artadvisor"
    label = "Art Advisor"

    getFormValues = classmethod(collectionMeta)
    isShown = classmethod(always)
    isEnabled = classmethod(isAllowedEditForm)
    getLink = classmethod(getEditLink)

    fields = collectionArtAdvisorFields
    persist = classmethod(persistCollectionMeta)
