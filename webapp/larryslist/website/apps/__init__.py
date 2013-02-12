from jsonclient.routing import FunctionRoute, App, ClassRoute, JSON_FORM_ATTRS, JSON_HANDLER_ATTRS, route_factory
from larryslist.website.apps import search, cart
from pyramid.httpexceptions import HTTPFound

from . import contexts, index, auth

ROUTE_LIST = [
    FunctionRoute   ("website_index"             , "/", contexts.WebsiteRootContext, index.index, "index.html")
    , ClassRoute    ("website_login"             , "/login", contexts.WebsiteRootContext, auth.LoginHandler, "auth/form.html", view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("website_logout"            , "/logout", contexts.WebsiteRootContext, auth.logout, None)
    , ClassRoute    ("website_signup"            , "/signup", contexts.WebsiteRootContext, auth.SignupHandler, "auth/form.html", view_attrs=JSON_FORM_ATTRS)
    , ClassRoute    ("website_password"          , "/ajax/templates/password.html", contexts.WebsiteRootContext, auth.PasswordHandler, "auth/password.html", view_attrs=JSON_FORM_ATTRS)
    , ClassRoute    ("website_password_reset"    , "/password/reset/:token", contexts.WebsiteRootContext, auth.PasswordResetHandler, "auth/form.html", view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("website_join_checkemail"   , "/signup/checkemail", contexts.WebsiteRootContext, auth.join_checkemail, "json", {'xhr':True})
    , FunctionRoute ("website_search"            , "/search", contexts.WebsiteRootContext, search.index, "search/index.html")
    , FunctionRoute ("website_cart"              , "/cart", contexts.WebsiteRootContext, cart.index, "cart/index.html")
    , FunctionRoute ("website_cart_save"         , "/cart/save", contexts.WebsiteRootContext, cart.save, "json", {'xhr':True})

    , FunctionRoute ("website_checkout"             , "/checkout", contexts.WebsiteRootContext, cart.checkout, "cart/checkout.html")
    , ClassRoute    ("website_checkout_join"        , "/checkout/join", contexts.WebsiteRootContext, cart.CheckoutLoginHandler, "cart/login.html", view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("website_checkout_options_ajax", "/ajax/templates/payment/options.html", contexts.WebsiteRootContext, cart.checkout_options, "cart/ajax/options.html")
    , ClassRoute    ("website_checkout_set_option"  , "/checkout/option", contexts.WebsiteRootContext, cart.SetOptionsHandler, None, view_attrs=JSON_FORM_ATTRS)
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
