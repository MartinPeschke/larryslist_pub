from jsonclient.cached import CachedLoader
from larryslist.lib.baseviews import RootContext
from larryslist.models import ClientTokenProc
from larryslist.models.config import ConfigModel
from pyramid.decorator import reify


GetAdminConfigProc = ClientTokenProc("/admin/config", root_key="Config", result_cls = ConfigModel)
config_loader = CachedLoader(GetAdminConfigProc, "REPORTS_CONFIG_CACHE")


class ReportsRootContext(RootContext):
    static_prefix = "/reports/static/"
    app_label = 'reports'

    @reify
    def config(self):
        return config_loader.get(self.request)

    @reify
    def client_token(self):
        return self.request.globals.reports.clientToken

    def is_allowed(self, request):
        return True
