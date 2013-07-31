
class BaseEPayMod(Persistent):

    def __init__(self):
        self._enabled = False
        self._title = ""
        self._id = ""

    def getId(self):
        return self._id

    def getTitle(self):
        return self._title

    def setTitle(self, title):
        self._title = title


class BaseTransaction(Persistent):

    def __init__(self):
        pass

    def getId(self):
        return""

    def getTransactionHTML(self):
        return ""

    def getTransactionHTMLModif(self):
        return ""

    def isChangeable(self):
        return False

class WorldPayMod(object):

    def __init__(self, date=None, url="", instId="", cartId="", testMode=""):
        self._title = "worldpay"
        self._id = "WorldPay"
        self._url = url
        self._instId =instId
        self._description = ""#"EuroPython Registration"
        self._testMode = testMode
        self._textCallBackSuccess = ""
        self._textCallBackCancelled = ""

    def getId(self):
        try:
            if self._id:
                pass
        except AttributeError, e:
            self._id="WorldPay"
        return self._id


    def getTitle(self):
        return self._title

    def setTitle(self, title):
        self._title = title


    def getInstId(self):
        try:
            return self._instId
        except:
            self._instId = ""
        return self._instId

    def setInstId(self, instId):
        self._instId = instId

    def getTextCallBackSuccess(self):
        try:
            return self._textCallBackSuccess
        except:
            self._textCallBackSuccess = ""
        return self._textCallBackSuccess

    def setTextCallBackSuccess(self, txt):
        self._textCallBackSuccess = txt

    def getTextCallBackCancelled(self):
        try:
            return self._textCallBackCancelled
        except:
            self._textCallBackCancelled = ""
        return self._textCallBackCancelled

    def setTextCallBackCancelled(self, txt):
        self._textCallBackCancelled = txt


    def getDescription(self):
        try:
            return self._description
        except:
            self._description = ""
        return self._description

    def setDescription(self, description):
        self._description = description

    def getTestMode(self):
        try:
            return self._testMode
        except:
            self._testMode = ""
        return self._testMode

    def setTestMode(self, testMode):
        self._testMode = testMode


    def setValues(self, data):
        self.setTitle(data.get("title", "epayment"))
        self.setUrl(data.get("url", ""))
        self.setInstId(data["instId"])
        self.setDescription(data["description"])
        self.setTestMode(data["testMode"])
        self.setTextCallBackSuccess(data.get("APResponse", "epayment"))
        self.setTextCallBackCancelled(data.get("CPResponse", "epayment"))

    def getFormHTML(self,price,currency,conf,registrant,lang = "en_US"):
        """build the registration form to be send to worldPay"""
        url_confirm=self._url_confirm #localUrlHandlers.UHPayConfirmWorldPay.getURL()
        url_cancel_return=self._url_cancel #localUrlHandlers.UHPayCancelWorldPay.getURL(registrant)
        url = self._url
        if isinstance(self._url, urlHandlers.URLHandler):
            url = self._url.getURL()
        #raise "%s"%(str(["", registrant.getCountry(), registrant.getPhone(), registrant.getEmail()]))
        s="""<form action="%s" method=POST>
             <td align="center"><input type=submit value="Proceed to %s"/></td>
             <input type=hidden name="instId" value="%s" />
             <input type=hidden name="cartId" value="%s"/>
             <input type=hidden name="amount" value="%s" />
             <input type=hidden name="currency" value="%s" />
             <input type=hidden name="desc" value="%s" />
             <INPUT TYPE=HIDDEN NAME=MC_callback VALUE="%s" />
             <input type=hidden name="M_shopperId" value="%s">
             <input type=hidden name="M_EPaymentName" value="WorldPay">
             <input type=hidden name="M_requestTag" value="confirm">
             <input type=hidden name="testMode" value="%s" />
             <input type=hidden name="name" value="%s %s"/>
             <input type=hidden name="address" value="%s"/>
            <input type=hidden name="postcode" value="%s"/>
            <input type=hidden name="country" value="%s"/>
            <input type=hidden name="tel" value="%s" />
            <input type=hidden name="email" value="%s"/>
            </form>
        """%(url, self.getTitle(), self._instId, self.getCartId(), "%.2f"%prix, Currency, self._description, url_confirm, self._conf.getId(), registrant.getId(), self._testMode, registrant.getFirstName(),registrant.getSurName(),\
                registrant.getAddress(),"", registrant.getCountry(), registrant.getPhone(), registrant.getEmail())
        return s

    def getUrl(self):
        return self._url

    def setUrl(self,url):
        self._url=url

    def getConfModifEPaymentURL(self, conf):
        return localUrlHandlers.UHConfModifEPaymentWorldPay.getURL(conf)

# World pay transaction

class TransactionWorldPay(BaseTransaction):
    """Transaction information which is accessible via Registrant.getTransactionInfo()"""

    def __init__(self,params):
        BaseTransaction.__init__(self)
        self._Data=params

    def getId(self):
        try:
            if self._id:
                pass
        except AttributeError, e:
            self._id="worldpay"
        return self._id

    def getTransactionHTML(self):
        return"""<table>
                          <tr>
                            <td align="right"><b>Payment with:</b></td>
                            <td align="left">WorldPay</td>
                          </tr>
                          <tr>
                            <td align="right"><b>Payment date:</b></td>
                            <td align="left">%s</td>
                          </tr>
                          <tr>
                            <td align="right"><b>TransactionID:</b></td>
                            <td align="left">%s</td>
                          </tr>
                          <tr>
                            <td align="right"><b>Amount:</b></td>
                            <td align="left">%s %s</td>
                          </tr>
                          <tr>
                            <td align="right"><b>Name:</b></td>
                            <td align="left">%s</td>
                          </tr>
                  </table>"""%(self._Data["payment_date"],self._Data["transId"], self._Data["amount"], \
                             self._Data["currency"], self._Data["name"])

    def getTransactionTxt(self):
        """this is used for notification email """
        return"""
\tPayment with:WorldPay\n
\tPayment Date:%s\n
\tPayment ID:%s\n
\tOrder Total:%s %s\n
\tName n:%s
"""%(self._Data["payment_date"],self._Data["transId"], self._Data["amount"], \
                             self._Data["currency"], self._Data["name"])



def getPayMod():
    return WorldPayMod()

def getPayModClass():
    return WorldPayMod