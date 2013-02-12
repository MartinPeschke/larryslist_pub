from larryslist.lib.formlib.formfields import BaseForm, ConfigChoiceField, REQUIRED, EmailField, PasswordField, PlainHeadingField, StringField, CheckboxField, CheckboxPostField
from larryslist.website.apps.auth import LoginForm, SignupForm


class PaymentOptionField(ConfigChoiceField):
    template = "larryslist:website/templates/cart/ajax/optionfield.html"

    def isSelected(self, option, value, request):
        if not value: value = request.session.get('PREFERRED_OPTION')
        return option.getKey(request) == value

class PaymentOptionsForm(BaseForm):
    fields = [PaymentOptionField("option", None, "PaymentOption", default_none = False)]
    action_label = "Buy your plan now"
    @classmethod
    def on_success(cls, request, values):
        request.session['PREFERRED_OPTION'] = values['option']
        return {'success':True, 'redirect':request.fwd_url("website_checkout")}

class JoinLoginForm(LoginForm):
    fields = [
        EmailField("email", "Email", REQUIRED)
        , PasswordField("pwd", "Password", REQUIRED)
    ]
    @classmethod
    def on_success(cls, request, values):
        result = super(JoinLoginForm, cls).on_success(request, values)
        if result.get("success"):
            return {'success':True, 'redirect':request.fwd_url("website_checkout")}
        else:
            return result

class JoinSignupForm(SignupForm):
    @classmethod
    def on_success(cls, request, values):
        result = super(JoinSignupForm, cls).on_success(request, values)
        if result.get("success"):
            return {'success':True, 'redirect':request.fwd_url("website_checkout")}
        else:
            return result

class CheckoutForm(BaseForm):
    classes = 'form-horizontal form-validated'
    action_label = "Buy your plan now"
    fields = [
        PaymentOptionField("option", None, "PaymentOption", default_none = False)
        , PlainHeadingField("Credit Card")
        , StringField("ccNumber", "Number", REQUIRED)
        , StringField("CVC", "CVV", REQUIRED)
        , StringField("expiryMonth", "Expiration", REQUIRED)
        , StringField("expiryYear", None, REQUIRED)
        , PlainHeadingField("Billing address")
        , StringField("lastName", "Name", REQUIRED)
        , StringField("firstName", "Surname", REQUIRED)
        , StringField("line1", "Street", REQUIRED)
        , StringField("postCode", "Zip Code", REQUIRED)
        , StringField("city", "City", REQUIRED)
        , StringField("country", "Country", REQUIRED)
        , CheckboxPostField("agreeTOS", u"Yes, I have read the Terms and Conditions and Agree.")
    ]
    @classmethod
    def on_success(cls, request, values):
        return {}