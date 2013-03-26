from jsonclient.routing import FunctionRoute, RedirectRoute, App, route_factory
from larryslist.reports.apps import contexts, handlers
from pyramid.httpexceptions import HTTPNotFound



class ReportsSettings(object):
    key = "reports"
    def __init__(self, settings):
        self.clientToken = settings['backend.token']

ROUTE_LIST = [
    RedirectRoute  ("reports_home"         , "/", to_route="reports_user_actions")
    , FunctionRoute("reports_user_actions" , "/user/actions", contexts.ReportsRootContext, handlers.user_actions, "user_actions.html")

]
ROUTE_MAP = {r.name:r for r in ROUTE_LIST}

def notfound(request):
    return HTTPNotFound('Not found!')


def includeme(config):
    route_factory('larryslist', ROUTE_LIST, App("reports"), config, template_path_prefix = 'reports')

    settings = config.registry.settings
    settings['g'].setSettings(ReportsSettings, settings)

