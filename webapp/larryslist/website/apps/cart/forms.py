from larryslist.lib.formlib.formfields import BaseForm, ConfigChoiceField, REQUIRED, EmailField, PasswordField
from larryslist.website.apps.auth import LoginForm, SignupForm


class PaymentOptionsForm(BaseForm):
    fields = [ConfigChoiceField("option", None, "PaymentOption")]

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

