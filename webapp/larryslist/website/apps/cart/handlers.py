from larryslist.lib.formlib.handlers import FormHandler
from larryslist.website.apps.cart.forms import PaymentOptionsForm, JoinLoginForm, JoinSignupForm, SpendCreditsForm, PLAN_SELECTED_TOKEN
from larryslist.website.apps.contexts import logged_in
from larryslist.website.apps.models import SpendCreditProc
from pyramid.decorator import reify
from pyramid.renderers import render_to_response




def checkout_arbiter(context, request):
    if context.user.isAnon():
        if not request.session.get(PLAN_SELECTED_TOKEN):
            request.fwd("website_checkout_plan_select")
        else:
            request.fwd("website_checkout_join")
    elif not len(context.cart.getItems()):
        request.fwd("website_search")
    elif context.cart.canSpend(context.user):
        request.fwd("website_purchase")
    else:
        if not request.session.get(PLAN_SELECTED_TOKEN):
            request.fwd("website_checkout_plan_select")
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

def straight_purchase(context, request):
    collectors = context.cart.getItems()
    if not collectors:
        request.fwd("website_cart")
    elif not context.cart.canSpend(context.user):
        request.fwd("website_checkout_arbiter")
    else:
        values = {'token': context.user.token, 'Collector':collectors}
        SpendCreditProc(request, values)
        if request.session.get(PLAN_SELECTED_TOKEN):
            del request.session[PLAN_SELECTED_TOKEN]
        context.cart.empty()
        request.fwd("website_index")



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


