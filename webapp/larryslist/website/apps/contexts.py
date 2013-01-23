from jsonclient.cached import CachedLoader
from larryslist.website.apps.models import WebsiteConfigModel
from larryslist.lib.baseviews import RootContext
from larryslist.models import ClientTokenProc
from pyramid.decorator import reify


GetWebConfigProc = ClientTokenProc("/web/config", root_key="Config", result_cls = WebsiteConfigModel)
config_loader = CachedLoader(GetWebConfigProc, "WEBSITE_CONFIG_CACHE")


class WebsiteRootContext(RootContext):
    static_prefix = "/web/static/"
    app_label = 'website'

    @reify
    def config(self):
        return config_loader.get(self.request)

    @reify
    def client_token(self):
        return self.request.globals.website.clientToken
