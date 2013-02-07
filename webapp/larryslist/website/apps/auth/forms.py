from jsonclient.backend import DBMessage
import formencode
from larryslist.lib.baseviews import GenericSuccessMessage
from larryslist.lib.formlib.formfields import BaseForm, EmailField, PasswordField, Placeholder, REQUIRED, StringField, HtmlAttrs
from larryslist.website.apps.auth.models import LoginProc, SignupProc, PasswordRequestProc, UpdatePasswordProc, ResendRequestProc

__author__ = 'Martin'



class LoginForm(BaseForm):
    id="login"
    label ="Login"
    action_label = "Login"
    fields = [
        EmailField("email", None, attrs = Placeholder("Email", required = True))
        , PasswordField("pwd", None, attrs = Placeholder("Password", required = True))
    ]
    @classmethod
    def on_success(cls, request, values):
        try:
            user = LoginProc(request, values)
        except DBMessage, e:
            return {'success':False, 'errors':{'email': "Unknown email or password!"}}
        return {'success':True, 'redirect': request.fwd_url("website_index")}


class SignupHandler(BaseForm):
    id="signup"
    label = "Signup"
    action_label = "Signup"
    fields = [
        StringField("name", "Name", REQUIRED)
        , EmailField("email", "Email", HtmlAttrs(required = True, data_validation_url = '/signup/checkemail'))
        , PasswordField("pwd", "Password", REQUIRED)
        , PasswordField("pwdconfirm", "Confirm password", REQUIRED)
    ]
    chained_validators = [formencode.validators.FieldsMatch('pwd', 'pwdconfirm')]
    @classmethod
    def on_success(cls, request, values):
        try:
            user = SignupProc(request, values)
        except DBMessage, e:
            if e.message == 'EMAIL_TAKEN':
                return {'success':False, 'errors':{'email': "Email already registered!"}}
            else:
                return {'success':False, 'errors':{'email': e.message}}
        return {'success':True, 'redirect':request.fwd_url("website_index")}



class PasswordForgotHandler(BaseForm):
    id="password"
    label = "Password forgot"
    action_label = "Submit"
    fields = [
        EmailField("email", "Email", REQUIRED)
    ]
    @classmethod
    def on_success(cls, request, values):
        email = values['email']
        try:
            if values.get('isResend'):
                ResendRequestProc(request, {'email':email})
            else:
                PasswordRequestProc(request, {'email':email})
        except DBMessage, e:
            if e.message in ['NO_USER', 'NO_USER_WITH_THIS_EMAIL', 'NO_OWNER_WITH_THIS_EMAIL']:
                errors = {"email": "Unknown email address."}
                return {'values' : values, 'errors':errors}
            elif e.message == "TOKEN_SET_IN_LAST_24_HOURS":
                values['isResend'] = True
                return {'values' : values, 'errors':{'email': "Email has been sent in last 24 hours!"}}
            else: raise e
        return {"success":True, "message":"An email to reset your password has been sent to: {email}!".format(email = email)}


class PasswordResetForm(BaseForm):
    id = "pwdreset"
    label = "Password reset"
    action_label = "Save"
    fields = [
        PasswordField("pwd", "New Password", REQUIRED)
        , PasswordField("pwdconfirm", "Confirm New Password", REQUIRED)
    ]
    chained_validators = [formencode.validators.FieldsMatch('pwd', 'pwdconfirm')]
    def on_success(self, request, values):
        try:
            UpdatePasswordProc(request, {'token':request.root.user.token, 'pwd':values['pwd']})
        except DBMessage:
            raise # HORROR HAPPENED
        request.session.flash(GenericSuccessMessage("Your password has been changed. You can now log in using your new password."), "generic_messages")
        request.fwd("website_index")