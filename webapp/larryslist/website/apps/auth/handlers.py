from larryslist.lib.formlib.handlers import FormHandler
from larryslist.website.apps.auth.forms import LoginForm, SignupHandler

__author__ = 'Martin'



class LoginHandler(FormHandler):
    form = LoginForm

class SignupHandler(FormHandler):
    form = SignupHandler