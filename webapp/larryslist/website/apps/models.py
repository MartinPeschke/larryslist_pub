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
    label = TextField()

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
    LABEL = ['One time', 'Basic Package', 'Premium Package']
    _PaymentOption = ListField(DictField(PaymentOptionModel), name='PaymentOption')
    @reify
    def PaymentOption(self):
        po = self._PaymentOption[:3]
        for i, p in enumerate(po):
            p.label = self.LABEL[i]
        return po
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


class PaymentModel(Mapping):
    paymentRef = TextField()
    amount = IntegerField()
    currency = TextField()
    shopperRef = TextField()
    shopperEmail = TextField()


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


CreatePurchaseCreditProc = ClientTokenProc("/web/credit/buy", result_cls=PaymentModel, root_key="Payment")
CheckPurchaseCreditProc = ClientTokenProc("/web/credit/paymentResult", result_cls=PaymentStatusModel, root_key="PaymentStatus")
SpendCreditProc = LoggingInProc("/web/credit/spend")


GetCollectorProc = ClientTokenProc("/web/user/getcollector", result_cls=FullCollectorModel, root_key="Collector")


import sqlite3 as lite
conn = None
def get_connection():
    if not conn:
        conn = lite.connect('/server/www/larryslist/live/transactions.db')
    return conn

class SimpleDB(object):
    sql_create = ""
    table_exists = "SELECT name FROM sqlite_master WHERE type='table' AND name='%s';"
    table_name = ""

    def __init__(self):
        self.conn = get_connection() 
        self._create_table()

    def get_cursor(self):
        return self.conn.cursor()

    def _check_table_exists(self):
        cur = self.get_cursor()
        sql = self.table_exists % self.table_name
        cur.execute(sql)
        rows = cur.fetchall()
        return rows and (rows[0][0] != self.table_name)

    def _create_table(self):
        if not self._check_table_exists():
            cur = self.get_cursor()
            cur.execute(self.sql_create)

    def _drop_table(self):
        pass


class PaymentTransaction(SimpleDB):
    sql_create = "CREATE TABLE payment_transaction(cartId VARCHAR(50) PRIMARY KEY, userToken VARCHAR(50), planToken VARCHAR(50), shopperRef VARCHAR(50), credit INTEGER, validated BOOLEAN, transId VARCHAR(50), transStatus VARCHAR(50), ipAddress VARCHAR(25));"
    table_name = "payment_transaction"
    sql_insert = "INSERT INTO payment_transaction(cartId, userToken, planToken, shopperRef, credit) VALUES (?,?,?,?,?);"
    sql_update = "UPDATE payment_transaction SET validated=?, transId=?, transStatus=?, ipAddress=? WHERE cartId=?;"
    sql_retrieve = "SELECT cartId, userToken, planToken, shopperRef, credit, validated, transId, transStatus, ipAddress FROM payment_transaction WHERE cartId=?"

    def __init__(self, cartId="", shopperRef=""):
        super(PaymentTransaction, self).__init__()

        self.userToken = ""
        self.planToken = ""
        self.cartId = ""
        self.shopperRef = ""
        self.credit = ""
        self.validated = False
        self.transId = ""
        self.transStatus = ""
        self.ipAddress = ""

        if cartId and shopperRef:
            #TODO: look for shoppperRef too?
            self._retrieve_cart(cartId)

    def create(self, userToken, planToken, cartId, shopperRef, credit):
        self.userToken = userToken
        self.planToken = planToken
        self.cartId = cartId
        self.shopperRef = shopperRef
        self.credit = credit
        self.__insert()

    def __insert(self):
        cur = self.get_cursor()
        cur.execute(sql_insert,(self.cartId,self.userToken,self.planToken,self.shopperRef,self.credit))

    def _retrieve_cart(self, cartId):
        cur = self.get_cursor()
        cur.execute(sql_retrieve,(cartId,))
        row = cur.fetchone()
        if row != None:
            self.cartId = row[0]
            self.userToken = row[1]
            self.planToken = row[2]
            self.shopperRef = row[3]
            self.credit = row[4]
            self.validated = row[5]
            self.transId = row[6]
            self.transStatus = row[7]
            self.ipAddress = row[8]

    def validate_transaction(self, userToken, transId, transStatus, ipAddress):
        #validate user token
        #validate by cartId and shopperRef
        cur = self.get_cursor()
        valid = True #TODO !!
        if valid:
            cur.execute(sql_update,(valid,transId, transStatus, ipAddress,self.cartId))
            self._retrieve_cart(self.cartId)
        return valid


class UserCredits(SimpleDB):
    pass


class CreditPaymentManager(object):
    def addTransaction(self, shopperRef, cartId):
        pass

    def validateCredit(self):
        pass

    def spendCredit(self):
        pass


class UserCreditsManager(object):
    def getUserCredits(self):
        pass

    def canSpend(self, credits):
        pass

    def spendCredits(self, credits):
        pass

