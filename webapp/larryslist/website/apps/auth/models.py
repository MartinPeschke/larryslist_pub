from jsonclient import Mapping, TextField, IntegerField
from larryslist.models import ClientTokenProc
import simplejson

SESSION_KEY = 'WEBSITE_USER'

class UserModel(Mapping):
    token = TextField()
    name = TextField()
    email = TextField()
    credit = IntegerField(default = 300)
    def isAnon(self):
        return self.token is None
    def getCredits(self):
        return self.credit / 100

    def toJSON(self, stringify = True):
        return simplejson.dumps(self.unwrap(sparse = True))


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


SignupProc = LoggingInProc("/user/signup")
LoginProc = LoggingInProc("/user/login")
PasswordRequestProc = ClientTokenProc("/user/forgotpwd")
ResendRequestProc = ClientTokenProc("/user/resendForgotPwd")
UpdatePasswordProc = ClientTokenProc("/user/updatePwd")
PasswordTokenVerifyProc = ClientTokenProc("/user/token", root_key = "User", result_cls = UserModel)

CheckEmailExistsProc = ClientTokenProc('/user/emailavailable')