import base64
from datetime import datetime, timedelta
import hashlib
import hmac
import urllib
from larryslist.lib.baseviews import GenericErrorMessage, GenericSuccessMessage
from larryslist.website.apps.cart import PLAN_SELECTED_TOKEN
import logging
from larryslist.website.apps.models import CreatePurchaseCreditProc, CheckPurchaseCreditProc, RefreshUserProfileProc, SpendCreditProc, \
                                        PaymentTransaction, UserCredits
from pyramid.renderers import render_to_response

log = logging.getLogger(__name__)

REQUEST_ORDER = ["paymentAmount","currencyCode","shipBeforeDate","merchantReference"
                    ,"skinCode","merchantAccount","sessionValidity","shopperEmail"
                    ,"shopperReference","recurringContract","allowedMethods","blockedMethods"
                    ,"shopperStatement","merchantReturnData","billingAddressType","offset"]
RESULT_ORDER = ["authResult", "pspReference", "merchantReference", "skinCode", "merchantReturnData"]


def get_signature(secret, params, sign_order = None):
    sign_order = sign_order or REQUEST_ORDER
    sign_base = ''.join([unicode(params.get(k, "")) for k in sign_order])
    hm = hmac.new(secret, sign_base, hashlib.sha1)
    return base64.encodestring(hm.digest()).strip()

def verify_signature(secret, params):
    merchantSig = params.get('merchantSig')
    if get_signature(secret, params, sign_order = RESULT_ORDER) == merchantSig:
        return params['merchantReturnData']
    else:
        return None

def get_request_parameters(standard_params, params):
    sign_base = standard_params.copy()
    sign_base["shipBeforeDate"] = (datetime.now() + timedelta(1)).strftime("%Y-%m-%d")
    sign_base["sessionValidity"] = (datetime.now() + timedelta(0, 1800)).strftime("%Y-%m-%dT%H:%M:%SZ")
    sign_base.update(params)
    return sign_base




def checkout_preview(context, request):
    """
    Checkout for Worldpay based on checkout_handler function
    """
    settings = request.globals.website
    
    installationId="301925"
    url="https://secure-test.worldpay.com/wcc/purchase"
    planToken = request.session.get(PLAN_SELECTED_TOKEN)
    plan = context.config.getPaymentOption(planToken)
    payment = CreatePurchaseCreditProc(request, {'userToken':context.user.token, 'paymentOptionToken': plan.token})
    #validator = PaymentTransaction()
    #validator.create(context.user.token, plan.token, payment.paymentRef, payment.shopperRef, plan.credit)
    standard_params = {}#settings.adyenParams.copy()
    
    formatCurrency = lambda v: v[:-2]+"."+v[-2:]


    redirect_params = {
        "amount": formatCurrency(unicode(payment.amount))
        ,"currency": "EUR"
        ,"lang":'en_US'
        ,"cartId" : payment.paymentRef
        ,"M_shopperReference" : payment.shopperRef
        ,"M_planToken" : request.session.get(PLAN_SELECTED_TOKEN)
        ,"email" : payment.shopperEmail
        ,"instId" : installationId
        ,"resURL":request.fwd_url("website_checkout_result")
        ,"testMode":"100"
        ,"noLanguageMenu": "true"
        ,"hideCurrency": "true"
    }

    params = get_request_parameters(standard_params, redirect_params)
    urlparams = '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in params.iteritems()])

    if request.session.get(PLAN_SELECTED_TOKEN):
        del request.session[PLAN_SELECTED_TOKEN]
    request.fwd_raw("%s?%s" % (url, urlparams))


def checkout_handler(context, request):
    settings = request.globals.website

    planToken = request.session.get(PLAN_SELECTED_TOKEN)
    plan = context.config.getPaymentOption(planToken)
    payment = CreatePurchaseCreditProc(request, {'userToken':context.user.token, 'paymentOptionToken': plan.token})
    standard_params = settings.adyenParams.copy()

    redirect_params = {
        "paymentAmount":unicode(payment.amount)
        ,"currencyCode":payment.currency
        ,"shopperLocale":'en_US'
        ,'allowedMethods': 'visa,mc,amex'
        ,"merchantReference" : payment.paymentRef
        ,"shopperReference" : payment.shopperRef
        ,"shopperEmail" : payment.shopperEmail
        ,"resURL":request.fwd_url("website_checkout_result")
    }

    params = get_request_parameters(standard_params, redirect_params)
    urlparams = '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in params.iteritems()])

    if request.session.get(PLAN_SELECTED_TOKEN):
        del request.session[PLAN_SELECTED_TOKEN]
    request.fwd_raw("%s?%s&merchantSig=%s" % (settings.adyenURL, urlparams, urllib.quote(get_signature(settings.adyenSecret, params))))


def payment_result_handler(context, request):
    log.info( 'PAYMENT RETURN from External: %s' , request.params )
    merchantReference = request.params.get('cartId')
    shopperReference = request.params.get('M_shopperReference')
    planToken = request.params.get('M_planToken') 
    paymentmethod =  request.params.get('cardType')
    params = request.params.mixed()
    p = lambda r,v: r.params.get(v)
    methods = {'Visa':"VISA",'Amex':'AMEX','MasterCard':'MC'}
    params["paymentRef"] = merchantReference
    params["shopperRef"] = shopperReference
    params["shopperEmail"] = request.params.get('email')
    params["amount"] = request.params.get('authAmount').replace(".","")
    params["year_price"] =  p(request,"amount").replace(".","")
    try:
        params["method"] =  methods[p(request,"cardType")]
    except:
        params["method"] = "ELV"
    params["payment_ref"] = merchantReference
    params["saveDetails"] = "0"
    params["currency"] =  p(request,"authCurrency")
    params["userToken"] =  context.user.token
    params["transactionId"] =  p(request,"transId")

    sss = ", , , , , , , , , , , , , , , , , , "


    #result = CheckPurchaseCreditProc(request, params)
    #if result.success:  #TODO: WorldPay save the credits locally
    
    #validator = PaymentTransaction(merchantReference, shopperReference)
    #if validator.validate_transaction(context.user.token, p(request,"transId"), p(request,"transStatus"), p(request,"ipAddress")):

    s = " ('installation' 'msgType' 'region' 'authAmountString' 'desc' 'tel' 'address1' 'countryMatch' 'address2' 'cartId' 'address3' 'callbackPW' 'lang' 'rawAuthCode' 'transStatus' 'amountString' 'authCost' 'currency' 'installation' 'amount' 'M_shopperReference' 'wafMerchMessage', 'countryString' 'displayAddress', 'transTime','name' 'testMode' 'routeKey' 'ipAddress' 'fax' 'rawAuthMessage' 'instId' 'AVS' 'compName' 'authAmount' 'postcode' 'cardType' 'cost' 'authCurrency' 'country' 'charenc' 'email' 'address' 'transId' 'msgType' 'town' 'authMode'"
    ss = "token, interval, amount, year_price, method, method_id, payment_ref, payment, email, user_id, option, new_credit_id, credit, number, saveDetails "
    

    if True:  # Should check if the transaction is valid
        settings = request.globals.website

        plan = context.config.getPaymentOption(planToken)

        #save credits
        #credits = UserCredits()
        #credits.create(userId,credits)
        
        ########## IMPORTANT ALEX
        #This is the code that calls the payment procedure
        plan = context.config.getPaymentOption(planToken)
        payment = CreatePurchaseCreditProc(request, {'userToken':context.user.token, 'paymentOptionToken': plan.token})
        #End code

        RefreshUserProfileProc(request, {'token':context.user.token})
        request.session.flash(GenericSuccessMessage("Payment Successful!"), "generic_messages")
        if not len(context.cart.getItems()):
            request.fwd("website_index_member")
        elif True: #context.cart.canSpend(context.user):
            values = {'token': context.user.token, 'Collector':[{'id': c.id} for c in context.cart.getCollectors()]}
            SpendCreditProc(request, values)
            context.cart.empty()
            if request.session.get(PLAN_SELECTED_TOKEN):
                del request.session[PLAN_SELECTED_TOKEN]
            request.fwd("website_index_member")
        else:
            request.session.flash(GenericErrorMessage("Not enough credits to purchase all profiles."), "generic_messages")
            request.fwd("website_cart")
    else:
        request.session.flash(GenericErrorMessage("Payment Failed!"), "generic_messages")
        request.fwd("website_cart")