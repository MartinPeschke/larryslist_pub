import logging
from jsonclient.routing import FunctionRoute, RedirectRoute, App, route_factory
from larryslist.reports.apps import contexts, handlers
from pyramid.httpexceptions import HTTPNotFound

log = logging.getLogger(__name__)

class Report(object):
    def __init__(self, name, url, slug, icon):
         self.name = name
         self.url = url
         self.slug = slug
         self.icon = icon

class ReportsSettings(object):
    key = "reports"
    reports = []
    def __init__(self, settings):
        self.clientToken = settings['backendToken']
        rS = settings.get('reports', {})
        self.reports = [Report(**v) for k,v in sorted(rS.items())]
        self.reportMap = {r.slug:r for r in self.reports}

ROUTE_LIST = [
    RedirectRoute  ("reports_home"         , "/", to_route="reports_user_actions")
    , FunctionRoute("reports_user_actions" , "/user/actions", contexts.ReportsRootContext, handlers.user_actions, "user_actions.html")
    , FunctionRoute("reports_report" , "/:slug/report", contexts.ReportsRootContext, handlers.reports, "reports.html")

]
ROUTE_MAP = {r.name:r for r in ROUTE_LIST}

def notfound(request):
    return HTTPNotFound('Not found!')


def includeme(config):
    route_factory('larryslist', ROUTE_LIST, App("reports"), config, template_path_prefix = 'reports')

    settings = config.registry.settings
    settings['g'].setSettings(ReportsSettings, settings)

