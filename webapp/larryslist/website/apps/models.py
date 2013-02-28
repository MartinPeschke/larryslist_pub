from operator import methodcaller
from jsonclient import ListField, DictField, Mapping, TextField, IntegerField, BooleanField
from larryslist.lib import i18n
from larryslist.models import ClientTokenProc
from larryslist.models.config import ConfigModel
import simplejson


class PaymentOptionModel(Mapping):
    PERIOD = 'year'
    credit = IntegerField()
    price = IntegerField()
    token = TextField()
    preferred = BooleanField()

    def getValue(self, request): return self.token
    def getKey(self, request): return self.token

    def getCredits(self):
        return self.credit
    def getFormattedPrice(self, request):
        return i18n.format_currency(self.price / 100, 'EUR', request)
    def getSavedAmount(self, request):
        return i18n.format_currency(50, 'EUR', request)
    def getPerCreditAmount(self, request):
        return i18n.format_currency(int(self.price / self.credit), 'EUR', request)

class WebsiteConfigModel(ConfigModel):
    PaymentOption = ListField(DictField(PaymentOptionModel))
    def getPaymentOptions(self):
        options = self.PaymentOption
        options[1].preferred = True
        return options





#  ============================= CART SECTION =============================




class LocationModel(Mapping):
    name = TextField()
    token = TextField()

class AddressModel(Mapping):
    Country = DictField(LocationModel)
    Region = DictField(LocationModel)
    City = DictField(LocationModel)

class CollectorModel(Mapping):
    id = IntegerField()
    status = TextField()
    initials = TextField()
    picture = TextField()
    rank = TextField()
    subscribers = TextField()
    completion = TextField()
    Address = ListField(DictField(AddressModel))
    def getName(self):
        return self.initials
    def getAddress(self):
        if not len(self.Address): return ''
        addr = self.Address[0]
        if not addr.Region or not addr.Country: return ''
        return u"{region}, {country}".format(region = addr.Region.name, country = addr.Country.name)



class WebsiteCart(object):
    Collectors = []

    def setContent(self, json):
        self.Collectors = json.get('Collectors')
    def getContent(self, stringify = False):
        cart = self.Collectors
        return simplejson.dumps({'Collectors':cart})

    def getItems(self):
        return self.Collectors
    def getCollectors(self):
        return map(CollectorModel.wrap, self.Collectors)
    def canSpend(self, user):
        return user.getCredits() >= len(self.getItems()) > 0
    def empty(self):
        self.Collectors = []


class PaymentStatusModel(Mapping):
    success = BooleanField()
    message = TextField()


#  ============================= USER SECTION =============================


SESSION_KEY = 'WEBSITE_USER'

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

class UserModel(Mapping):
    token = TextField()
    name = TextField()
    email = TextField()
    credit = IntegerField(default = 0)
    cardNumber = TextField()
    Collector = ListField(DictField(CollectorModel))

    def isAnon(self):
        return self.token is None
    def getCredits(self):
        return self.credit

    def toJSON(self, stringify = True):
        json = self.unwrap(sparse = True)
        json['Collector'] = [{'id': c['id']} for c in json.pop("Collector", []) if c.get('id')]
        return simplejson.dumps(json)

    def hasSavedDetails(self):
        return bool(self.cardNumber)

    def discardSavedDetails(self):
        self.cardNumber = None
        return True



SignupProc = LoggingInProc("/user/signup")
LoginProc = LoggingInProc("/user/login")
PasswordRequestProc = ClientTokenProc("/user/forgotpwd")
ResendRequestProc = ClientTokenProc("/user/resendForgotPwd")
UpdatePasswordProc = ClientTokenProc("/user/updatePwd")
PasswordTokenVerifyProc = ClientTokenProc("/user/token", root_key = "User", result_cls = UserModel)
CheckEmailExistsProc = ClientTokenProc('/user/emailavailable')
RefreshUserProfileProc = LoggingInProc("/user/profile")


PurchaseCreditProc = ClientTokenProc("/web/credit/buy", result_cls=PaymentStatusModel, root_key="PaymentStatus")
SpendCreditProc = LoggingInProc("/web/credit/spend")