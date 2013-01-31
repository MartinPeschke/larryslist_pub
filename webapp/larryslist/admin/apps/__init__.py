from jsonclient.routing import FunctionRoute, App, ClassRoute, RedirectRoute, JSON_FORM_ATTRS, route_factory
from larryslist.admin.apps import collector, auth, settings

from . import contexts, index
from pyramid.view import forbidden_view_config


class AdminSettings(object):
    key = "admin"
    def __init__(self, settings):
        self.clientToken = settings['backend.token']

ROUTE_LIST = [
    FunctionRoute   ("admin_index"                   , "/", contexts.AdminAuthedContext, index.index, "index.html")
    , ClassRoute    ("admin_login"                   , "/login", contexts.AdminRootContext, auth.LoginHandler, "auth/login.html", view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("admin_logout"                  , "/logout", contexts.AdminRootContext, auth.logout, None)
    , ClassRoute    ('admin_reset_password'          , '/password/reset/:token', contexts.AdminRootContext, auth.PasswordResetHandler, "auth/password_reset.html", view_attrs = JSON_FORM_ATTRS)

    # ============================== COLLECTOR/COLLECTIONS =========================
    , ClassRoute    ("admin_collector_create"        , "/collector/create", contexts.AdminAuthedContext, collector.CollectorCreate, "collector/form.html", view_attrs=JSON_FORM_ATTRS)
    , ClassRoute    ("admin_collector_edit"          , "/collector/edit/:collectorId/:stage", contexts.AdminAuthedContext, collector.CollectorEdit, "collector/form.html", view_attrs=JSON_FORM_ATTRS)
    , ClassRoute    ("admin_collection_create"       , "/collection/create/:collectorId", contexts.AdminAuthedContext, collector.CollectionCreate, "collector/form.html", view_attrs=JSON_FORM_ATTRS)
    , ClassRoute    ("admin_collector_add_collector" , "/collection/add/:collectorId/collector", contexts.AdminAuthedContext, collector.AddCollectorHandler, "collector/collectoradd.html", view_attrs=JSON_FORM_ATTRS)
    , ClassRoute    ("admin_collection_edit"         , "/collection/edit/:collectorId/:stage", contexts.AdminAuthedContext, collector.CollectionEdit, "collector/form.html", view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("admin_sources_save"            , "/sources/save/:collectorId", contexts.AdminAuthedContext, collector.sources_save, "json", {'xhr': True, 'request_method':'POST'})
    , ClassRoute    ("admin_document_upload"         , "/documents/upload/:collectorId", contexts.AdminAuthedContext, collector.DocumentUpload, "collector/documents.html", view_attrs=JSON_FORM_ATTRS)

    # =============================== ADMIN-SETTINGS ===============================
    , ClassRoute    ("admin_settings_feeder_create"  , "/settings/feeder/create", contexts.AdminContext, settings.FeederHandler, "settings/feeder_create.html", view_attrs=JSON_FORM_ATTRS)



]
ROUTE_MAP = {r.name:r for r in ROUTE_LIST}

@forbidden_view_config()
def forbidden(request):
    request.fwd("admin_login")


def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(AdminSettings, settings)
    if settings['g'].is_debug:
        config.add_static_view('admin/static', '../static', cache_max_age=3600)

    route_factory('larryslist', ROUTE_LIST, App("admin"), config, template_path_prefix = 'admin')
