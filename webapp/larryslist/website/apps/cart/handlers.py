from larryslist.lib.formlib.handlers import FormHandler
from larryslist.website.apps.cart.forms import PaymentOptionsForm, JoinLoginForm, JoinSignupForm, CheckoutForm, SpendCreditsForm
from larryslist.website.apps.contexts import logged_in
from pyramid.renderers import render_to_response


def checkout_arbiter(context, request):
    if context.user.isAnon():
        request.fwd("website_checkout_join")
    elif not len(context.cart.getItems()):
        request.fwd("website_search")
    elif context.cart.canSpend(context.user):
        request.fwd("website_cart")
    else:
        request.fwd("website_checkout")


class CheckoutHandler(FormHandler):
    form = CheckoutForm
    @logged_in("website_checkout_join")
    def __init__(self, context, request):
        super(CheckoutHandler, self).__init__(context, request)

    def pre_fill_values(self, request, result):
        result['options'] = self.context.config.getPaymentOptions()
        return result



class CheckoutLoginHandler(FormHandler):
    forms = [JoinLoginForm, JoinSignupForm]


def checkout_options(context, request):
    handler = PaymentOptionsHandler(context, request)
    result = handler.getForm()
    result['options'] = context.config.getPaymentOptions()
    return result

class PaymentOptionsHandler(FormHandler):
    form = PaymentOptionsForm
    def getForm(self):
        result = super(PaymentOptionsHandler, self).GET()
        result['form'] = self.form
        result['query'] = ''
        return result

    def GET(self):
        return render_to_response("larryslist:website/templates/search/index.html", self.getForm(), self.request)
    def ajaxGET(self):
        return render_to_response("larryslist:website/templates/cart/ajax/options.html", self.getForm(), self.request)


def save_cart(context, request):
    context.cart.setContent(request.json_body)
    return {'success':True}


class SpendCreditsHandler(FormHandler):
    form = SpendCreditsForm
