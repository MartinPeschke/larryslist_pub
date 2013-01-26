from jsonclient.cached import CachedLoader
from larryslist.admin.apps.auth.models import getStandardUser
from .models import AdminConfigModel
from larryslist.lib.baseviews import RootContext
from larryslist.models import ClientTokenProc


from pyramid.decorator import reify

GetAdminConfigProc = ClientTokenProc("/config", root_key="Config", result_cls = AdminConfigModel)
config_loader = CachedLoader(GetAdminConfigProc, "ADMIN_CONFIG_CACHE")


class AdminRootContext(RootContext):
    static_prefix = "/admin/static/"
    app_label = 'admin'

    @reify
    def config(self):
        return config_loader.get(self.request)

    @reify
    def client_token(self):
        return self.request.globals.admin.clientToken

    def is_allowed(self, request):
        return True

    @reify
    def user(self):
        return getStandardUser()
