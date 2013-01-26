from jsonclient.routing import FunctionRoute, App, ClassRoute, RedirectRoute, JSON_FORM_ATTRS, route_factory
from larryslist.admin.apps import collector

from . import contexts, index

class AdminSettings(object):
    key = "admin"
    def __init__(self, settings):
        self.clientToken = settings['backend.token']

ROUTE_LIST = [
    FunctionRoute   ("admin_index"                   , "/", contexts.AdminRootContext, index.index, "index.html")
    , ClassRoute    ("admin_collector_create"        , "/collector/create", contexts.AdminRootContext, collector.CreateCollectorHandler, "collector/collector.html", view_attrs=JSON_FORM_ATTRS)
    , ClassRoute    ("admin_collector_edit"          , "/collector/edit/:collectorId/:stage", contexts.AdminRootContext, collector.EditHandler, "collector/collector.html", view_attrs=JSON_FORM_ATTRS)

    , ClassRoute    ("admin_collection_create"       , "/collection/create/:collectorId", contexts.AdminRootContext, collector.CollectionCreate, "collector/collection.html", view_attrs=JSON_FORM_ATTRS)
    , ClassRoute    ("admin_collection_add_collector", "/collection/add/:collectorId/collector", contexts.AdminRootContext, collector.AddCollectorHandler, "collector/collectoradd.html", view_attrs=JSON_FORM_ATTRS)

    , ClassRoute    ("admin_collection_edit"         , "/collection/edit/:collectorId/:stage", contexts.AdminRootContext, collector.CollectionEdit, "collector/collection.html", view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("admin_sources_save"            , "/sources/save/:collectorId", contexts.AdminRootContext, collector.sources_save, "json", {'xhr': True, 'request_method':'POST'})



]
ROUTE_MAP = {r.name:r for r in ROUTE_LIST}



def includeme(config):
    settings = config.registry.settings
    settings['g'].setSettings(AdminSettings, settings)
    if settings['g'].is_debug:
        config.add_static_view('admin/static', '../static', cache_max_age=3600)

    route_factory('larryslist', ROUTE_LIST, App("admin"), config, template_path_prefix = 'admin')
