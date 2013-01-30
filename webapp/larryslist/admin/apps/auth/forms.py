from jsonclient.backend import DBMessage
from larryslist.admin.apps.auth.models import AdminForgotPwdProc, AdminLoginProc
from larryslist.lib.formlib.formfields import BaseForm, EmailField, StringField, PasswordField, REQUIRED

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
            return {'success':False, 'errors': {'email': e.message}}
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
        user = None #AdminForgotPwdProc
        if user:
            return {'success':True, 'message':"Email has been sent to {email}, please check your inbox!".format(**values)}
        else:
            return {'success': False, 'errors':{'email':'Unknown email.'}}