from jsonclient import Mapping, TextField
from larryslist.models import ClientTokenProc

SESSION_KEY = 'WEBSITE_USER'

class UserModel(Mapping):
    token = TextField()
    name = TextField()
    email = TextField()
    def isAnon(self):
        return self.token is None

def LoggingInProc(path, db_messages = []):
    sproc = ClientTokenProc(path, root_key='User', result_cls=UserModel)
    def f(request, data):
        result = sproc(request, data)
        request.session[SESSION_KEY] = request.user = result
        return result
    return f

def getUserFromSession(request):
    return request.session.get(SESSION_KEY, UserModel(token=None, name = 'Anon'))

def logoutAdmin(request):
    if SESSION_KEY in request.session:
        del request.session[SESSION_KEY]
    request.fwd("website_index")


LoginProc = LoggingInProc("/user/login")
PasswordRequestProc = LoggingInProc("/user/forgotpwd")
ResendRequestProc = ClientTokenProc("/user/resendForgotPwd")
UpdatePasswordProc = ClientTokenProc("/user/updatePwd")
PasswordTokenVerifyProc = ClientTokenProc("/user/token", root_key = "User", result_cls = UserModel)