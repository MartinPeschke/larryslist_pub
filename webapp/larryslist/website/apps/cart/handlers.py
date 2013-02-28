from larryslist.lib.formlib.handlers import FormHandler
from larryslist.website.apps.cart.forms import PaymentOptionsForm, JoinLoginForm, JoinSignupForm, CheckoutForm, SpendCreditsForm, SavedDetailsCheckoutForm, PLAN_SELECTED_TOKEN
from larryslist.website.apps.contexts import logged_in
from pyramid.renderers import render_to_response




def checkout_arbiter(context, request):
    if not request.session.get(PLAN_SELECTED_TOKEN):
        request.fwd("website_checkout_plan_select")
    elif context.user.isAnon():
        request.fwd("website_checkout_join")
    elif not len(context.cart.getItems()):
        request.fwd("website_search")
    elif context.cart.canSpend(context.user):
        request.fwd("website_cart")
    else:
        request.fwd("website_checkout")

def checkout_plan_select(context, request):
    handler = PaymentOptionsHandler(context, request)
    result = handler.getForm()
    result['options'] = context.config.getPaymentOptions()
    return result



def discard_saved_details(context, request):
    context.user.discardSavedDetails()
    request.fwd("website_checkout")

class CheckoutHandler(FormHandler):
    forms = [CheckoutForm, SavedDetailsCheckoutForm]
    @logged_in("website_checkout_join")
    def __init__(self, context, request):
        super(CheckoutHandler, self).__init__(context, request)

    def pre_fill_values(self, request, result):
        result['options'] = self.context.config.getPaymentOptions()
        result['values'][self.getForm().id] = {'number': request.root.user.cardNumber}
        return result

    def getForm(self):
        return self.forms[self.context.user.hasSavedDetails()]


class CheckoutLoginHandler(FormHandler):
    forms = [JoinLoginForm, JoinSignupForm]

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
