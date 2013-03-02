from jsonclient.routing import FunctionRoute, App, ClassRoute, JSON_FORM_ATTRS, JSON_HANDLER_ATTRS, route_factory
from larryslist.website.apps import search, cart, collector
from pyramid.httpexceptions import HTTPFound

from . import contexts, index, auth

ROUTE_LIST = [
    FunctionRoute   ("website_index"             , "/", contexts.WebsiteRootContext, index.index, "index.html")
    , FunctionRoute ("website_index_member"      , "/home", contexts.WebsiteAuthedContext, index.index_member, "index_member.html")
    , ClassRoute    ("website_login"             , "/login", contexts.WebsiteRootContext, auth.LoginHandler, "auth/form.html", view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("website_logout"            , "/logout", contexts.WebsiteRootContext, auth.logout, None)
    , ClassRoute    ("website_signup"            , "/signup", contexts.WebsiteRootContext, auth.SignupHandler, "auth/form.html", view_attrs=JSON_FORM_ATTRS)
    , ClassRoute    ("website_password"          , "/ajax/templates/password.html", contexts.WebsiteRootContext, auth.PasswordHandler, "auth/password.html", view_attrs=JSON_FORM_ATTRS)
    , ClassRoute    ("website_password_reset"    , "/password/reset/:token", contexts.WebsiteRootContext, auth.PasswordResetHandler, "auth/form.html", view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("website_join_checkemail"   , "/signup/checkemail", contexts.WebsiteRootContext, auth.join_checkemail, "json", {'xhr':True})
    , FunctionRoute ("website_search"            , "/search", contexts.WebsiteRootContext, search.index, "search/index.html")

    , ClassRoute    ("website_cart"              , "/cart", contexts.WebsiteRootContext, cart.SpendCreditsHandler, "cart/index.html", view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("website_cart_save"         , "/cart/save", contexts.WebsiteRootContext, cart.save_cart, "json", {'xhr':True})

    , ClassRoute    ("website_checkout"             , "/checkout", contexts.WebsiteRootContext, cart.CheckoutHandler, "cart/checkout.html", view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("website_purchase"             , "/purchase", contexts.WebsiteRootContext, cart.straight_purchase, None)
    , FunctionRoute ("website_checkout_arbiter"     , "/checkout/arbiter", contexts.WebsiteRootContext, cart.checkout_arbiter, None)
    , ClassRoute    ("website_checkout_join"        , "/checkout/join", contexts.WebsiteRootContext, cart.CheckoutLoginHandler, "cart/login.html", view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("website_checkout_plan_select" , "/checkout/plan", contexts.WebsiteRootContext, cart.checkout_plan_select, "cart/plan_select.html")
    , ClassRoute    ("website_checkout_set_option"  , "/checkout/option", contexts.WebsiteRootContext, cart.PaymentOptionsHandler, None, view_attrs=JSON_FORM_ATTRS)
    , FunctionRoute ("website_discard_saved_details", "/checkout/discard", contexts.WebsiteRootContext, cart.discard_saved_details, None)


    , FunctionRoute ("website_collector_personal"   , "/collector/:collectorId/:name", contexts.WebsiteCollectorContext, collector.index, "collector/index.html")
    , FunctionRoute ("website_collector_collection"   , "/collector/:collectorId/:name/collection", contexts.WebsiteCollectorContext, collector.index, "collector/collection.html")
    , FunctionRoute ("website_collector_art"   , "/collector/:collectorId/:name/art", contexts.WebsiteCollectorContext, collector.index, "collector/art.html")
    , FunctionRoute ("website_collector_news"   , "/collector/:collectorId/:name/news", contexts.WebsiteCollectorContext, collector.index, "collector/news.html")
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
