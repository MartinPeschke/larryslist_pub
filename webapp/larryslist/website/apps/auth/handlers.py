from jsonclient.backend import DBMessage
from larryslist.lib.baseviews import GenericErrorMessage
from larryslist.lib.formlib.handlers import FormHandler
from larryslist.website.apps.auth.forms import LoginForm, SignupHandler, PasswordForgotHandler, PasswordResetForm
from larryslist.website.apps.auth.models import CheckEmailExistsProc, PasswordTokenVerifyProc, SESSION_KEY
from pyramid.httpexceptions import HTTPFound

__author__ = 'Martin'




def join_checkemail(context, request):
    try:
        CheckEmailExistsProc(request, {"email": request.params.get('signup.email')})
    except DBMessage, e:
        return "Email already taken"
    else:
        return True

def logout(context, request):
    session = request.session
    if SESSION_KEY in session:
        del session[SESSION_KEY]
    if request.params.get('furl'):
        request.fwd_raw(request.params.get('furl'))
    else:
        request.fwd("website_index")


class LoginHandler(FormHandler):
    form = LoginForm
class SignupHandler(FormHandler):
    form = SignupHandler
class PasswordHandler(FormHandler):
    form = PasswordForgotHandler

class PasswordResetHandler(FormHandler):
    form = PasswordResetForm
    def is_valid(self):
        request = self.request
        try:
            user = PasswordTokenVerifyProc(request, request.matchdict)
            self.context.user = user
        except DBMessage, e:
            request.session.flash(GenericErrorMessage("Invalid Link. Please check the link or request a new password forgot email."), "generic_messages")
            request.fwd("website_index")
        else:
            return True

    def GET(self):
        if self.is_valid():
            return super(PasswordResetHandler, self).GET()

    def POST(self):
        if self.is_valid():
            return super(PasswordResetHandler, self).POST()


    def ajax(self):
        try:
            self.is_valid()
            result = self.validate_json()
            return result
        except HTTPFound, e: # success case
            return {'redirect': e.location, "errorMessage": ",".join(self.request.session.pop_flash())}