from larryslist.lib.baseviews import BaseHandler
from larryslist.models.collector import CollectorMetaModel, GetCollectorMetaProc, CollectionMetaModel, GetCollectionMetaProc
from larryslist.website.apps.models import GetCollectorProc
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPUnauthorized


class CollectorHandler(BaseHandler):
    def __init__(self, context, request):
        super(CollectorHandler, self).__init__(context, request)
        if not self.collector:
            raise HTTPUnauthorized()

    def GET(self):
        return {}

    @reify
    def collector(self):
        id = self.request.matchdict.get('collectorId')
        user = self.context.user
        col = user.getCollector(id)
        if not col: return None
        else:
            return GetCollectorProc(self.request, {'id': id, 'userToken': user.token})

    @reify
    def collectionMeta(self):
        if self.collector.Collection:
            result = CollectionMetaModel.wrap(GetCollectionMetaProc(self.request, str(self.collector.Collection.id)))
        else:
            result = None
        return result

    @reify
    def collectorMeta(self):
        result = CollectorMetaModel.wrap(GetCollectorMetaProc(self.request, str(self.collector.id)))
        return result

    def is_allowed(self, request):
        user = self.context.user
        if user.isAnon():
            request.fwd("website_index")
        elif not self.collector:
            raise HTTPUnauthorized()
        else:
            return True
