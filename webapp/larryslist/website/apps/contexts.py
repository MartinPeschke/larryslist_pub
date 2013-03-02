from jsonclient.cached import CachedLoader
from larryslist.models.collector import GetCollectionMetaProc, CollectionMetaModel, CollectorMetaModel, GetCollectorMetaProc
from larryslist.website.apps.auth.forms import LoginForm
from larryslist.website.apps.models import getUserFromSession, WebsiteCart, WebsiteConfigModel, GetCollectorProc
from larryslist.lib.baseviews import RootContext
from larryslist.models import ClientTokenProc
from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPUnauthorized

GetWebConfigProc = ClientTokenProc("/web/config", root_key="Config", result_cls = WebsiteConfigModel)
config_loader = CachedLoader(GetWebConfigProc, "WEBSITE_CONFIG_CACHE")


class logged_in(object):
    def __init__(self, auth_route):
        self.auth_route = auth_route

    def __call__(self, wrapped):
        try:
            self.__doc__ = wrapped.__doc__
        except: # pragma: no cover
            pass
        def wrapped_f(obj, context, request):
            if context.user.isAnon():
                request.fwd(self.auth_route)
            else:
                return wrapped(obj, context, request)
        return wrapped_f


class WebsiteRootContext(RootContext):
    static_prefix = "/web/static/"
    app_label = 'website'

    @reify
    def config(self):
        return config_loader.get(self.request)

    @reify
    def user(self):
        return getUserFromSession(self.request)

    def getLoginForm(self):
        return LoginForm(), {}, {}

    @reify
    def cart(self):
        session = self.request.session
        cart = session.get("website_cart", WebsiteCart())
        if "website_cart" not in session:
            session["website_cart"] = cart
        return cart

class WebsiteAuthedContext(WebsiteRootContext):
    def is_allowed(self, request):
        if self.user.isAnon():
            request.fwd("website_checkout_join")
        else:
            return True

class WebsiteCollectorContext(WebsiteAuthedContext):
    @reify
    def collector(self):
        id = self.request.matchdict.get('collectorId')
        col = self.user.getCollector(id)
        if not col: return None
        else:
            return GetCollectorProc(self.request, {'id': id, 'userToken': self.user.token})

    @reify
    def collectionMeta(self):
        result = CollectionMetaModel.wrap(GetCollectionMetaProc(self.request, str(self.collector.Collection.id)))
        return result

    @reify
    def collectorMeta(self):
        result = CollectorMetaModel.wrap(GetCollectorMetaProc(self.request, str(self.collector.id)))
        return result

    def is_allowed(self, request):
        if self.user.isAnon():
            request.fwd("website_index")
        elif not self.collector:
            raise HTTPUnauthorized()
        else:
            return True