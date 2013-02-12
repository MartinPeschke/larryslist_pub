from jsonclient.cached import CachedLoader
from larryslist.website.apps.auth.forms import LoginForm
from larryslist.website.apps.auth.models import getUserFromSession
from larryslist.website.apps.cart.models import WebsiteCart
from larryslist.website.apps.models import WebsiteConfigModel
from larryslist.lib.baseviews import RootContext
from larryslist.models import ClientTokenProc
from pyramid.decorator import reify

GetWebConfigProc = ClientTokenProc("/web/config", root_key="Config", result_cls = WebsiteConfigModel)
config_loader = CachedLoader(GetWebConfigProc, "WEBSITE_CONFIG_CACHE")

class WebsiteRootContext(RootContext):
    static_prefix = "/web/static/"
    app_label = 'website'

    @reify
    def config(self):
        return config_loader.get(self.request)

    @reify
    def user(self):
        return getUserFromSession(self.request)

    def getLoginForm(self):
        return LoginForm(), {}, {}

    @reify
    def cart(self):
        session = self.request.session
        cart = session.get("website_cart", WebsiteCart())
        if "website_cart" not in session:
            session["website_cart"] = cart
        return cart
