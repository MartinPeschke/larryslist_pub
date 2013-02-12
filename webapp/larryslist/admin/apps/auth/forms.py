from jsonclient.backend import DBMessage
import formencode
from larryslist.admin.apps.auth.models import AdminLoginProc, UpdatePasswordProc, ResendRequestProc, PasswordRequestProc
from larryslist.lib.baseviews import GenericSuccessMessage
from larryslist.lib.formlib.formfields import BaseForm, EmailField, PasswordField, REQUIRED

__author__ = 'Martin'



class LoginForm(BaseForm):
    label = "Login"
    fields = [
        EmailField("email", "Email", REQUIRED)
        , PasswordField("pwd", "Password", REQUIRED)
    ]

    @classmethod
    def on_success(cls, request, values):
        try:
            user = AdminLoginProc(request, values)
        except DBMessage, e:
            msg = e.message
            if e.message == 'LOGIN_FAILED':
                msg = "Unknown email or password"
            return {'success':False, 'errors': {'email': msg}}
        else:
            return {'success':True, 'redirect': request.fwd_url("admin_index")}


class PasswordforgotForm(BaseForm):
    id = 'pwdforgot'
    label = "Forgot password"
    fields = [
        EmailField("email", "Email", REQUIRED)
    ]
    @classmethod
    def on_success(cls, request, values):
        email = values['email']
        try:
            if request.json_body.get('isResend'):
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
        request.session.flash(GenericSuccessMessage("An email to reset your password has been sent to: {email}!".format(**values)), "generic_messages")
        return {"success":True, "redirect":request.fwd_url("admin_login")}




class PasswordResetForm(BaseForm):
    successmsg = "Your password has been changed. You can now log in using your new password."
    fields = [
        PasswordField("pwd", "Password", REQUIRED)
        , PasswordField("pwdconfirm", "Confirm password", REQUIRED)
    ]

    chained_validators = [formencode.validators.FieldsMatch('pwd', 'pwdconfirm')]

    @classmethod
    def on_success(cls, request, values):
        try:
            UpdatePasswordProc(request, {'token':request.context.user.token, 'pwd':values['pwd']})
        except DBMessage:
            raise # HORROR HAPPENED
        request.session.flash(GenericSuccessMessage(cls.successmsg), "generic_messages")
        return {'success':True, 'redirect': request.fwd_url("admin_index"), 'message': cls.successmsg}
