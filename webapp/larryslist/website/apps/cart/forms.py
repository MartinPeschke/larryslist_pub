import formencode
from larryslist.lib.baseviews import GenericErrorMessage
from larryslist.lib.formlib.formfields import BaseForm, ConfigChoiceField, REQUIRED, EmailField, PasswordField, PlainHeadingField, StringField, CheckboxField, CheckboxPostField, CombinedField, HtmlAttrs
from larryslist.website.apps.auth import LoginForm, SignupForm
from larryslist.website.apps.models import RefreshUserProfileProc, SpendCreditProc


PLAN_SELECTED_TOKEN = "PLAN_SELECTED"

class PaymentOptionField(ConfigChoiceField):
    template = "larryslist:website/templates/cart/optionfield.html"

    def isSelected(self, option, value, request):
        if not value: value = request.session.get('PREFERRED_OPTION')
        return option.getKey(request) == value

class PaymentOptionsForm(BaseForm):
    fields = [PaymentOptionField("option", None, "PaymentOption", default_none = False)]
    action_label = "Buy your plan now"
    @classmethod
    def on_success(cls, request, values):
        request.session[PLAN_SELECTED_TOKEN] = values['option']
        return {'success':True, 'redirect':request.fwd_url("website_checkout_arbiter")}

class JoinLoginForm(LoginForm):
    fields = [
        EmailField("email", "Email", REQUIRED)
        , PasswordField("pwd", "Password", REQUIRED)
    ]
    @classmethod
    def on_success(cls, request, values):
        result = super(JoinLoginForm, cls).on_success(request, values)
        if result.get("success"):
            return {'success':True, 'redirect':request.fwd_url("website_checkout_arbiter")}
        else:
            return result

class JoinSignupForm(SignupForm):
    @classmethod
    def on_success(cls, request, values):
        result = super(JoinSignupForm, cls).on_success(request, values)
        if result.get("success"):
            return {'success':True, 'redirect':request.fwd_url("website_checkout_arbiter")}
        else:
            return result


class SpendCreditsForm(BaseForm):
    id="spend"

    @classmethod
    def on_success(cls, request, values):
        context = request.root
        values['token'] = context.user.token
        collectors = values.get('Collector')
        if not collectors:
            return {'success':False, 'message': "No Profiles selected"}
        elif not context.cart.canSpend(context.user):
            return {'success':False, 'message': "Insufficient credits"}
        else:
            SpendCreditProc(request, values)
            if request.session.get(PLAN_SELECTED_TOKEN):
                del request.session[PLAN_SELECTED_TOKEN]
            context.cart.empty()
        return {'success':True, 'redirect': request.fwd_url("website_index")}