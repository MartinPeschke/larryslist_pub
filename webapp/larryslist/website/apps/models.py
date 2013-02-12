from jsonclient import ListField, DictField, Mapping, TextField, IntegerField, BooleanField
from larryslist.lib import i18n
from larryslist.models.config import ConfigModel


class PaymentOptionModel(Mapping):
    PERIOD = 'year'
    credit = IntegerField()
    price = IntegerField()
    token = TextField()
    preferred = BooleanField()

    def getValue(self, request): return self.token
    def getKey(self, request): return self.token

    def getCredits(self):
        return self.credit / 100
    def getFormattedPrice(self, request):
        return i18n.format_currency(self.price / 100, 'EUR', request)
    def getSavedAmount(self, request):
        return i18n.format_currency(50, 'EUR', request)

class WebsiteConfigModel(ConfigModel):
    PaymentOption = ListField(DictField(PaymentOptionModel))
    def getPaymentOptions(self):
        options = self.PaymentOption
        options[1].preferred = True
        return options