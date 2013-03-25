import base64
from datetime import datetime, timedelta
import hashlib
import hmac
import urllib
from larryslist.lib.baseviews import GenericErrorMessage, GenericSuccessMessage
from larryslist.website.apps.cart import PLAN_SELECTED_TOKEN
import logging
from pyramid.renderers import render_to_response

log = logging.getLogger(__name__)

REQUEST_ORDER = ["paymentAmount","currencyCode","shipBeforeDate","merchantReference"
                    ,"skinCode","merchantAccount","sessionValidity","shopperEmail"
                    ,"shopperReference","recurringContract","allowedMethods","blockedMethods"
                    ,"shopperStatement","merchantReturnData","billingAddressType","offset"]
RESULT_ORDER = ["authResult", "pspReference", "merchantReference", "skinCode", "merchantReturnData"]

SECRET = 'PaulaAbnormal'
BASE_URL = 'https://test.adyen.com/hpp/pay.shtml'

def get_signature(params, sign_order = None):
    sign_order = sign_order or REQUEST_ORDER
    sign_base = ''.join([unicode(params.get(k, "")) for k in sign_order])
    hm = hmac.new(SECRET, sign_base, hashlib.sha1)
    return base64.encodestring(hm.digest()).strip()

def verify_signature(params):
    merchantSig = params.get('merchantSig')
    if get_signature(params, sign_order = RESULT_ORDER) == merchantSig:
        return params['merchantReturnData']
    else:
        return None

def get_request_parameters(standard_params, params):
    sign_base = standard_params.copy()
    sign_base["shipBeforeDate"] = (datetime.now() + timedelta(1)).strftime("%Y-%m-%d")
    sign_base["sessionValidity"] = (datetime.now() + timedelta(0, 1800)).strftime("%Y-%m-%dT%H:%M:%SZ")
    sign_base.update(params)
    return sign_base





def checkout_handler(context, request):
    planToken = request.session.get(PLAN_SELECTED_TOKEN)
    plan = context.config.getPaymentOption(planToken)
    price = plan.price

    standard_params = {"merchantAccount":'LarryslistDE', "skinCode":'6agGJOyq'}
    redirect_params = {
        "paymentAmount":'%s'%price
        ,"currencyCode":'EUR'
        ,"shopperLocale":'en_US'
        ,'allowedMethods': 'visa,mc,amex'
        ,"merchantReference" : 'YAY_NOW_{}'.format(datetime.now().strftime("%Y%m%d%H%M%S"))
        ,"resURL":request.fwd_url("website_checkout_result")
    }

    params = get_request_parameters(standard_params, redirect_params)
    urlparams = '&'.join(['%s=%s' % (k, urllib.quote(v)) for k,v in params.iteritems()])
    request.fwd_raw("%s?%s&merchantSig=%s" % (BASE_URL, urlparams, urllib.quote(get_signature(params))))


def payment_result_handler(context, request):
    log.info( 'PAYMENT RETURN from External: %s' , request.params )
    merchantReference = request.params.get('merchantReference')
    paymentmethod =  request.params.get('paymentMethod')
    if request.params.get('authResult') == 'AUTHORISED':
        request.session.flash(GenericSuccessMessage("Payment Successful!"), "generic_messages")
        return render_to_response('/contribution/payment_success.html', {}, request)
    else:
        request.session.flash(GenericErrorMessage("Payment Failed!"), "generic_messages")
        return render_to_response('/contribution/payment_fail.html', {}, request)