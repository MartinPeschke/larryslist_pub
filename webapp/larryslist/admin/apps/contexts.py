from operator import methodcaller
from jsonclient.cached import CachedLoader
from larryslist.admin.apps.auth.models import getUserFromSession
from .models import AdminConfigModel
from larryslist.lib.baseviews import RootContext
from larryslist.models import ClientTokenProc


from pyramid.decorator import reify
from pyramid.httpexceptions import HTTPForbidden
import simplejson

GetAdminConfigProc = ClientTokenProc("/config", root_key="Config", result_cls = AdminConfigModel)
config_loader = CachedLoader(GetAdminConfigProc, "ADMIN_CONFIG_CACHE")


class MenuItem(object):
    def __init__(self, onlyAdmin, route, label):
        self.label = label
        self.route = route
        self.onlyAdmin = onlyAdmin
    def isAllowed(self, context, request):
        return (not self.onlyAdmin) or self.onlyAdmin and context.user.isAdmin()

HEADER_MENU = [
    MenuItem(True, "admin_settings_feeder_create", "Add Feeder")
    , MenuItem(True, "admin_news_feed", "Add News")
]


class AdminRootContext(RootContext):
    static_prefix = "/admin/static/"
    app_label = 'admin'

    @reify
    def config(self):
        return config_loader.get(self.request)

    def configJSON(self):
        return simplejson.dumps(self.config.unwrap())

    def is_allowed(self, request):
        return True

    @reify
    def user(self):
        return getUserFromSession(self.request)

    header_menu = []



class AdminAuthedContext(AdminRootContext):
    def is_allowed(self, request):
        if self.user.isAnon():
            request.fwd("admin_login")
        else:
            return True

    @reify
    def header_menu(self):
        return filter(methodcaller("isAllowed", self, self.request), HEADER_MENU)

class AdminContext(AdminAuthedContext):
    def is_allowed(self, request):
        if self.user.isAdmin():
            return True
        else:
            raise HTTPForbidden()

    header_menu = HEADER_MENU
