class EPayment(Persistent):

    def __init__(self, conf, groupData=None):
        self._conf = conf
        if groupData is None:
            self.activated = False

        else:
            self.activated = groupData.get("activated", False)
        self.paymentDetails = ""
        self.paymentConditionsEnabled = False
        self.paymentConditions = EPaymentDefaultValues.getDefaultConditions()
        self.paymentSpecificConditions = ""
        self.payMods = {}
        self.enableSendEmailPaymentDetails=True

    def loadPlugins(self, initSorted=True):
        self.payMods = {}
        epaymentModules = PluginLoader.getPluginsByType("EPayment")
        for mod in epaymentModules:
            try:
                self.payMods[mod.pluginName] = mod.epayment.getPayMod()
            except:
                pass
        self._p_changed = 1
        #self.payMods["PayLater"] = PayLaterMod()
        if initSorted:
            self.initSortedModPay()

##        #Simple-SubForms
##        self.yellowPay = YellowPayMod()
##        self.payLater = PayLaterMod()
##        self.payPal = PayPalMod()
##        self.worldPay = WorldPayMod()
##        #All SortedForms

    def updatePlugins(self, initSorted=True):
        epaymentModules = PluginLoader.getPluginsByType("EPayment")
        changed = False
        for mod in epaymentModules:
            try:
                if not mod.pluginName in self.payMods.keys():
                    print "add mod %s"%mod
                    self.payMods[mod.pluginName] = mod.epayment.getPayMod()
                    print "%s"%self.payMods
                    changed = True
                else:
                    if not isinstance(self.payMods[mod.pluginName], mod.epayment.getPayModClass()):
                        #oldMod = self.payMods[mod.pluginName]
                        print "replace by mod %s"%mod
                        newMod = mod.epayment.getPayMod()
                        self.payMods[mod.pluginName] = newMod
                        changed = True
            except:
                pass
        if changed:
            self._p_changed = 1
        if initSorted:
            self.initSortedModPay()


    def initSortedModPay(self):
        try:
            self.payMods.values()
        except:
            self.loadPlugins(initSorted=False)
        self.updatePlugins(initSorted=False)
        self._sortedModPay = self.payMods.values()
        self._p_changed = 1

    def getPayModByTag(self, tag):
        try:
            if not self.payMods.keys():
                self.loadPlugins()
        except:
            self.loadPlugins()
        if tag in self.payMods.keys():
            return self.payMods[tag]
        self.updatePlugins()
        if tag in self.payMods.keys():
            return self.payMods[tag]
        return None

    def getConference(self):
        return self._conf
    getOwner = getConference

    def setConference(self, conf):
        self._conf = conf
    setOwner = setConference

    def getPaymentDetails(self):
        try:
            return self.paymentDetails
        except:
            self.paymentDetails = ""
        return self.paymentDetails

    def setPaymentDetails(self, txt):
        self.paymentDetails = txt

    def getPaymentSpecificConditions(self):
        try:
            return self.specificPaymentConditions
        except:
            self.specificPaymentConditions = ""
        return self.specificPaymentConditions

    def setPaymentSpecificConditions(self, txt):
        self.specificPaymentConditions = txt

    def getPaymentConditions(self):
        try:
            return self.paymentConditions
        except:
            self.paymentConditions = EPaymentDefaultValues.getDefaultConditions()
        return self.paymentConditions

    def setPaymentConditions(self, txt):
        self.paymentConditions = txt

    def arePaymentConditionsEnabled(self):
        try:
            if self.paymentConditionsEnabled:
                pass
        except Exception,e:
            self.paymentConditionsEnabled = False
        return self.paymentConditionsEnabled

    def setPaymentConditionsEnabled(self,v):
        self.paymentConditionsEnabled=v

    def hasPaymentConditions(self):
        if self.arePaymentConditionsEnabled():
            return True
        elif self.getPaymentSpecificConditions().strip()!="":
            return True
        return False

    def getConditions(self):
        if self.arePaymentConditionsEnabled() and self.getPaymentSpecificConditions().strip() == "":
            return "%s"%(self.getPaymentConditions())
        else:
            return "%s"%(self.getPaymentSpecificConditions())

    def getPaymentReceiptMsg(self):
        try:
            return self.receiptMsg
        except:
            self.receiptMsg = EPaymentDefaultValues.getDefaultReceiptMsg()
        return self.receiptMsg

    def setPaymentReceiptMsg(self, txt):
        self.receiptMsg = txt

    def getPaymentSuccessMsg(self):
        try:
            return self.successMsg
        except:
            self.successMsg = EPaymentDefaultValues.getDefaultSuccessMsg()
        return self.successMsg

    def setPaymentSuccessMsg(self, txt):
        self.successMsg = txt

    def isActivated(self):
        return self.activated

    def activate(self):
        self.activated = True

    def deactivate(self):
        self.activated = False

    def setActivated(self, value):
        self.activated = value

    def isMandatoryAccount(self):
        try:
            if self._mandatoryAccount:
                pass
        except AttributeError, e:
            self._mandatoryAccount = True
        return self._mandatoryAccount

    def setMandatoryAccount(self, v=True):
        self._mandatoryAccount = v

    def setTitle( self, newName ):
        self.title = newName.strip()

    def getTitle( self ):
        return self.title

    def isEnableSendEmailPaymentDetails(self):
        try:
            if self.enableSendEmailPaymentDetails:
                pass
        except AttributeError, e:
            self.enableSendEmailPaymentDetails=True
        return self.enableSendEmailPaymentDetails

    def setEnableSendEmailPaymentDetails(self, v=True):
        self.enableSendEmailPaymentDetails = v

##    def getModPayPal(self):
##        return self.payPal
##
##    def getModYellowPay(self):
##        try:
##            return self.yellowPay
##        except:
##            self.yellowPay = YellowPayMod()
##        return self.yellowPay
##
##    def getModPayLater(self):
##        try:
##            return self.payLater
##        except:
##            self.payPal = PayPalMod()
##        return self.payLater
##
##    def getModWorldPay(self):
##        try:
##            return self.worldPay
##        except:
##            self.worldPay = WorldPayMod()
##        return self.worldPay

    def getSortedModPay(self):
##        try:
##            if self._sortedModPay:
##                pass
##        except AttributeError,e:
##            self.initSortedModPay()
        self.updatePlugins()
        return self._sortedModPay

    def addToSortedModPay(self, form, i=None):
        if i is None:
            i=len(self.getSortedModPay())
        try:
            self.getSortedModPay().remove(form)
        except ValueError,e:
            pass
        self.getSortedModPay().insert(i, form)
        self.notifyModification()
        return True

    def removeFromSortedModPay(self, form):
        try:
            self.getSortedModPay().remove(form)
        except ValueError,e:
            return False
        self.notifyModification()
        return True

    def getModPayById(self, id):
        return self.getPayModByTag(id)
##        if id == "yellowpay":
##            return self.getModYellowPay()
##        if id == "paylater":
##            return self.getModPayLater()
##        if id == "paypal":
##            return self.getModPayPal()
##        if id == "worldPay":
##            return self.getModWorldPay()
##        return None


    def getLocator( self ):
        """Gives back (Locator) a globaly unique identification encapsulated in
            a Locator object for the RegistrationForm instance """
        if self.getConference() == None:
            return Locator()
        lconf = self.getConference().getLocator()
        return lconf


    def recover(self):
        TrashCanManager().remove(self)

    def notifyModification(self):
        self._p_changed=1
        self._conf.notifyModification()

class EPaymentDefaultValues:

    @staticmethod
    def getDefaultConditions():
        return """
CANCELLATION :

All refunds requests must be in writing by mail to the Conference Secretary as soon as possible.
The Conference committee reserves the right to refuse reimbursement of part or all of the fee in the case of late cancellation. However, each case of cancellation would be considered individually.
"""

    @staticmethod
    def getDefaultSuccessMsg():
        return """Congratulations, your payment was successful."""

    @staticmethod
    def getDefaultReceiptMsg():
        return """Please, see the summary of your order:"""

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

    def setEnabled(self, v):
        self._enabled = v

    def isEnabled(self):
        try:
            if self._enabled:
                pass
        except AttributeError, e:
            self._enabled = False
        return self._enabled

    def getFormHTML(self, price, currency, registrant, lang = "en_US"):
        """
        Returns the html form that will be used to send the information to the epayment server.
        """
        raise Exception("This method must be overloaded")

    def getConfModifEPaymentURL(self, conf):
        """
        For each plugin there is just one URL for all requests. The plugin will have its own parameters to manage different URLs (have a look to urlHandler.py). This method returns that general URL.
        """
        raise Exception("This method must be overloaded")

    def setValues(self, data):
        """ Saves the values coming in a dict (data) in the corresping class variables. (e.g. title, url, business, etc) """
        raise Exception("This method must be overloaded")


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

class WorldPayMod( BaseEPayMod ):

    def __init__(self, date=None):
        BaseEPayMod.__init__(self)
        self._title = "worldpay"
        self._id = "WorldPay"
        self._url = "https://select.worldpay.com/wcc/purchase"
        self._instId = ""#"70950"
        self._description = ""#"EuroPython Registration"
        self._testMode = ""#"100"
        self._textCallBackSuccess = ""
        self._textCallBackCancelled = ""

    def getId(self):
        try:
            if self._id:
                pass
        except AttributeError, e:
            self._id="WorldPay"
        return self._id

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

    def getFormHTML(self,prix,Currency,conf,registrant,lang = "en_US"):
        """build the registration form to be send to worldPay"""
        url_confirm=localUrlHandlers.UHPayConfirmWorldPay.getURL()
        url_cancel_return=localUrlHandlers.UHPayCancelWorldPay.getURL(registrant)
        url = self._url
        self._conf = registrant.getConference()
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
             <input type=hidden name="M_confId" value="%s">
             <input type=hidden name="M_registrantId" value="%s">
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
        """%(url, self.getTitle(), self._instId, registrant.getId(), "%.2f"%prix, Currency, self._description, url_confirm, self._conf.getId(), registrant.getId(), self._testMode, registrant.getFirstName(),registrant.getSurName(),\
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