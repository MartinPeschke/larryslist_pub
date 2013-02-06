from larryslist.lib.formlib.handlers import FormHandler
from larryslist.website.apps.auth.forms import LoginForm

__author__ = 'Martin'



class LoginHandler(FormHandler):
    forms =[LoginForm]