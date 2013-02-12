from larryslist.lib.formlib.handlers import FormHandler
from larryslist.website.apps.cart.forms import PaymentOptionsForm, JoinLoginForm, JoinSignupForm
from larryslist.website.apps.contexts import logged_in
from pyramid.renderers import render_to_response


def save(context, request):
    context.cart.setContent(request.json_body)
    return {'success':True}

def index(context, request):
    return {}


@logged_in("website_checkout_join")
def checkout(context, request):
    if not len(context.cart.getItems()):
        request.fwd("website_search")
    else:
        return {}


def checkout_options(context, request):
    handler = SetOptionsHandler(context, request)
    result = handler.getForm()
    result['options'] = context.config.getPaymentOptions()
    return result


class CheckoutLoginHandler(FormHandler):
    forms = [JoinLoginForm, JoinSignupForm]

class SetOptionsHandler(FormHandler):
    form = PaymentOptionsForm

    def getForm(self):
        result = super(SetOptionsHandler, self).GET()
        result['form'] = self.form
        result['query'] = ''
        return result

    def GET(self):
        return render_to_response("larryslist:website/templates/search/index.html", self.getForm(), self.request)
    def ajaxGET(self):
        return render_to_response("larryslist:website/templates/cart/ajax/options.html", self.getForm(), self.request)
