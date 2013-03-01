import formencode
from larryslist.lib.baseviews import GenericErrorMessage
from larryslist.lib.formlib.formfields import BaseForm, ConfigChoiceField, REQUIRED, EmailField, PasswordField, PlainHeadingField, StringField, CheckboxField, CheckboxPostField, CombinedField, HtmlAttrs
from larryslist.website.apps.auth import LoginForm, SignupForm
from larryslist.website.apps.models import RefreshUserProfileProc, PurchaseCreditProc, SpendCreditProc


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



class CheckoutForm(BaseForm):
    id = "new"
    classes = 'form-horizontal form-validated'
    action_label = "Purchase now"
    has_discard = False
    fields = [
        PlainHeadingField("Credit Card", tag="h5", classes="label-spacealike")
        , ConfigChoiceField("method", "Card Type:", "CardType", default_none=False)
        , StringField("holder", "Holder:", REQUIRED)
        , StringField("number", "Number:", REQUIRED, min = 13, max = 16)
        , StringField("cvs", "CVV:", attrs = HtmlAttrs(required = True) , min = 3, max = 4,input_classes='input-mini')
        , CombinedField([ConfigChoiceField("expiryMonth", None, "ExpiryMonth", default_none=False), ConfigChoiceField("expiryYear", None, "ExpiryYear", default_none=False)], "Expiration:", REQUIRED)
        , CheckboxPostField("agreeTOS", u"Yes, I have read the Terms and Conditions and Agree.", REQUIRED)
    ]
    @classmethod
    def extraOptions(cls, values):
        values['saveDetails'] = True
        return values
    @classmethod
    def on_success(cls, request, values):
        values['userToken'] = request.root.user.token
        values = cls.extraOptions(values)
        status = PurchaseCreditProc(request, values)
        if status.success == True:
            context = request.root
            RefreshUserProfileProc(request, {'token':request.root.user.token})

            if not len(context.cart.getItems()):
                request.fwd("website_index")
            elif context.cart.canSpend(context.user):
                values = {'token': context.user.token, 'Collector':[{'id': c.id} for c in context.cart.getCollectors()]}
                SpendCreditProc(request, values)
                context.cart.empty()
                request.fwd("website_index")
            else:
                request.session.flash(GenericErrorMessage("Not enough credits to purchase all profiles."), "generic_messages")
                request.fwd("website_cart")
        else:
            errors = {}
            if status.message == "PAYMENT_FAILED":
                errors = {"number": "Invalid payment data, please check card details."}
            elif status.message == "INVALID_CARD_NUMBER":
                errors = {"number": "Invalid card number"}
            elif status.message.startswith("validation 140"):
                errors = {"expiryYear": "Expiry date must be in the future"}
            elif status.message.startswith("validation 103"):
                errors = {"cvs": "CVC is not right length"}
            else:
                errors = {"number": "Invalid card number {}".format(status.message)}
            return {'success':False, "message":"Payment Failed", 'values':values, 'errors':errors}

class SavedDetailsCheckoutForm(CheckoutForm):
    id = "saved"
    has_discard = True
    fields = [
        PlainHeadingField("Use Saved Credit Card Details", tag="h5", classes="standard-padded-box")
        , StringField("number", "Saved Card", attrs = HtmlAttrs(readonly = True))
        , StringField("cvs", "CVV", attrs = HtmlAttrs(required = True) , min = 3, max = 4)
    ]

    @classmethod
    def extraOptions(cls, values):
        values['useSavedDetails'] = True
        return values


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
            context.cart.empty()
        return {'success':True, 'redirect': request.fwd_url("website_index")}