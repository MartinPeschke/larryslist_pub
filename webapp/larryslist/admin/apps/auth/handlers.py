from jsonclient.backend import DBMessage
from larryslist.admin.apps.auth.forms import LoginForm, PasswordforgotForm, PasswordResetForm
from larryslist.admin.apps.auth.models import logoutAdmin, PasswordTokenVerifyProc
from larryslist.lib.baseviews import GenericErrorMessage
from larryslist.lib.formlib.handlers import FormHandler
from paste.httpexceptions import HTTPFound

__author__ = 'Martin'

def logout(context, request): logoutAdmin(request)


class LoginHandler(FormHandler):
    forms = [LoginForm, PasswordforgotForm]

    def isFormActive(self, form):
        return form.id == self.forms[0].id


class PasswordResetHandler(FormHandler):
    form = PasswordResetForm
    def is_valid(self):
        try:
            user = PasswordTokenVerifyProc(self.request, self.request.matchdict)
            self.request.context.user = user
        except DBMessage, e:
            self.request.session.flash(GenericErrorMessage("Invalid Link. Please check the link or request a new password forgot email."), "generic_messages")
            return False
        else:
            return True

    def GET(self):
        if self.is_valid(): return super(PasswordResetHandler, self).GET()
        else: self.request.fwd("admin_login")

    def POST(self):
        if self.is_valid(): return super(PasswordResetHandler, self).POST()
        else: self.request.fwd("admin_login")
    def ajax(self):
        if self.is_valid(): return self.validate_json()
        else: return {'succces':False, 'redirect': self.request.fwd_url("admin_login")}

