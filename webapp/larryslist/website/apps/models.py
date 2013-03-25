from datetime import timedelta, datetime
from operator import methodcaller
from jsonclient import ListField, DictField, Mapping, TextField, IntegerField, BooleanField, DateTimeField
from larryslist.lib import i18n
from larryslist.models import ClientTokenProc
from larryslist.models.config import ConfigModel
from pyramid.decorator import reify
import simplejson

from larryslist.models.collector import CollectorModel as FullCollectorModel
from larryslist.models.collector import SimpleCollectorModel as CollectorModel


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
        return i18n.format_currency(10 * self.credit - self.price / 100, 'EUR', request)
    def getPerCreditAmount(self, request):
        return i18n.format_currency(int(self.price / 100 / self.credit), 'EUR', request)

class WebsiteConfigModel(ConfigModel):
    PaymentOption = ListField(DictField(PaymentOptionModel))

    @reify
    def optionMap(self):
        return {o.token: o for o in self.PaymentOption}
    def getPaymentOptions(self):
        options = self.PaymentOption
        options[1].preferred = True
        return options
    def getPaymentOption(self, token):
        return self.optionMap[token]



#  ============================= CART SECTION =============================






class WebsiteCart(object):
    Collectors = []

    def setContent(self, json):
        self.Collectors = json.get('Collectors', [])
    def getContent(self, stringify = False):
        cart = self.Collectors
        return simplejson.dumps({'Collectors':cart})

    def getItems(self):
        return self.Collectors or []
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
        request.session[SESSION_KEY] = request.root.user = result
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
    Collector = ListField(DictField(FullCollectorModel))

    def isAnon(self):
        return self.token is None
    def getCredits(self):
        return self.credit
    def toJSON(self, stringify = True):
        json = self.unwrap(sparse = True).copy()
        json['Collector'] = [{'id': c['id'], 'firstName':c['firstName'], 'lastName':c['lastName']} for c in json.pop("Collector", []) if c.get('id')]
        return simplejson.dumps(json)
    def hasSavedDetails(self):
        return bool(self.cardNumber)
    def discardSavedDetails(self):
        self.cardNumber = None
        return True
    def getCreditWithPlan(self, plan):
        return self.credit + plan.credit

    @reify
    def collectorMap(self):
        return {c.id: c for c in self.Collector}
    def getCollector(self, id):
        return self.collectorMap.get(int(id))
    def hasCollector(self, collector):
        return isinstance(self.collectorMap.get(collector.id), CollectorModel)

    def getCreditValidity(self, request):
        return i18n.format_date(datetime.now() + timedelta(356), request)

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


GetCollectorProc = ClientTokenProc("/web/user/getcollector", result_cls=FullCollectorModel, root_key="Collector")