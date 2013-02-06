from jsonclient.routing import FunctionRoute, App, ClassRoute, JSON_FORM_ATTRS, JSON_HANDLER_ATTRS, route_factory
from pyramid.httpexceptions import HTTPFound

from . import contexts, index, auth

ROUTE_LIST = [
    FunctionRoute   ("website_index"             , "/", contexts.WebsiteRootContext, index.index, "index.html")
    , ClassRoute    ("website_login"             , "/login", contexts.WebsiteRootContext, auth.LoginHandler, "auth/login.html")
]


class WebsiteSettings(object):
    key = "website"
    def __init__(self, settings):
        self.clientToken = settings['backend.token']
        self.gaTrackingCode= settings['ga_tracking_code']

def home_url(request):
    return request.fwd_url("website_index")

def home(request):
    raise HTTPFound(location = request.home_url)

def getLogoUrl(request):
    return '{}://{}{}img/logo.png'.format(request.scheme, request.host, request.root.root_statics)

ROUTE_MAP = {r.name:r for r in ROUTE_LIST}



def includeme(config):
    config.add_request_method(home_url, 'home_url', reify=True)
    config.add_request_method(home, 'home')

    settings = config.registry.settings
    settings['g'].setSettings(WebsiteSettings, settings)
    if settings['g'].is_debug:
        config.add_static_view('web/static', '../static', cache_max_age=3600)

    route_factory('larryslist', ROUTE_LIST, App("website"), config, template_path_prefix = 'website')
