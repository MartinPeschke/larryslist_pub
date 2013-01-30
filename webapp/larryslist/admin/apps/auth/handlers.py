from larryslist.admin.apps.auth.forms import LoginForm, PasswordforgotForm
from larryslist.admin.apps.auth.models import logoutAdmin
from larryslist.lib.formlib.handlers import FormHandler

__author__ = 'Martin'

def logout(context, request): logoutAdmin(request)


class LoginHandler(FormHandler):
    forms = [LoginForm, PasswordforgotForm]

    def isFormActive(self, form):
        return form.id == self.forms[0].id