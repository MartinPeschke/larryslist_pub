from jsonclient import Mapping, TextField
from jsonclient.backend import DBMessage
from larryslist.models import ClientTokenProc

__author__ = 'Martin'


SESSION_KEY = 'ADMIN_USER'

class AdminUser(Mapping):
    token = TextField()
    name = TextField()
    country = TextField()
    type = TextField()

    def isAnon(self):
        return self.token is None


def LoggingInProc(path, db_messages = []):
    sproc = ClientTokenProc(path, root_key='Feeder', result_cls=AdminUser)
    def f(request, data):
        result = sproc(request, data)
        request.session[SESSION_KEY] = request.user = result
        return result
    return f

def getUserFromSession(request):
    return request.session.get(SESSION_KEY, AdminUser(token=None, name = 'Anon'))

def logoutAdmin(request):
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]
    request.fwd("admin_login")



AdminLoginProc = LoggingInProc("/admin/feeder/login")
PasswordRequestProc = LoggingInProc("/admin/feeder/forgotpwd")
ResendRequestProc = ClientTokenProc("/admin/feeder/resendForgotPwd")
UpdatePasswordProc = ClientTokenProc("/admin/feeder/updatePwd")
PasswordTokenVerifyProc = ClientTokenProc("/admin/feeder/token", root_key = "Feeder", result_cls = AdminUser)