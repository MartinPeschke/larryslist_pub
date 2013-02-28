from datetime import datetime
from decimal import Decimal
from babel import negotiate_locale
from babel.numbers import format_currency as fc, format_decimal as fdec, get_currency_symbol, get_decimal_symbol, get_group_symbol, parse_number as pn
from babel.dates import format_date as fdate, format_datetime as fdatetime, format_time as ftime
from pyramid.i18n import TranslationStringFactory, get_localizer
import logging

log = logging.getLogger(__name__)

MEASURES = {"METRIC": {'m':"m", 'sqm':'m<sup>2</sup>', 'mins':'mins'}
            , "IMPERIAL": {'m':'yd', 'sqm':'ft<sup>2</sup>', 'mins':'mins'}}

def getMeasures(key, metric_unit='m'):
    return MEASURES[key][metric_unit]

default_currency = '&euro;'

def get_locale(request):
    return request._LOCALE_

def format_int_amount(number, request):
    if number is None:
        return ''
    number = float(number)/100
    if round(number) == number:
        return '%d' % int(number)
    else:
        fnumber = Decimal('%.2f' % number)
        return fdec(fnumber, format='#,##0.00', locale=get_locale(request))

def get_thous_sep(request):
    return get_group_symbol(locale=get_locale(request))
def get_dec_sep(request):
    return get_decimal_symbol(locale=get_locale(request))
def display_currency(currency, request):
    return get_currency_symbol(currency, locale=get_locale(request))
def format_currency(number, currency, request):
    if round(number) == number:
        return u'€{}'.format(int(number))
    else:
        fnumber = Decimal('%.2f' % number)
        return fc(fnumber, currency, locale = get_locale(request))

def parse_number(strNum, request):
    return pn(strNum, locale=get_locale(request))
def format_number(number, request):
    if number is None or number=="": return ""
    fnumber = Decimal('%.2f' % number)
    return fdec(fnumber, format='#,##0.##;-#', locale=get_locale(request))

def format_date(date, request, with_time = False, format="medium"):
    if not date: return ""
    if with_time:
        return fdatetime(date, format=format, locale=get_locale(request))
    else:
        return fdate(date, format=format, locale=get_locale(request))

def format_time(datetime, request, format="short"):
    if not datetime: return ""
    return ftime(datetime, format=format, locale=get_locale(request))



def parse_date_internal(date):
    return datetime.strptime(date, "%Y-%m-%d")

def format_date_internal(date):
    if not date: return ""
    return date.strftime('%Y-%m-%d')

def format_datetime_internal(dateTime):
    if not dateTime: return ""
    return dateTime.strftime('%Y-%m-%dT%H:%M:%S')

def format_short_date(date, request, with_time = False):
    return fdate(date, "d. MMM", locale=get_locale(request))








class DefaultLocaleNegotiator(object):
    def __init__(self, available_locales, default_locale_name):
        self.available_locales = available_locales
        self.default_locale_name = default_locale_name
        log.info("SETUP LOCALE NEGOTIATION WITH %s (%s)", self.available_locales, self.default_locale_name)
    
    def negotiate_locale(self, accept_langs):
        def normalize_locale(loc):
            return unicode(loc).replace('-', '_')
        langs = map(normalize_locale, accept_langs)
        return negotiate_locale(langs, self.available_locales, sep="_") or self.default_locale_name
    
    def __call__(self, request):
        if getattr(request,'_LOCALE_', None):
            locale_name = request._LOCALE_
        elif 'lang' not in request.session or request.session['lang'] not in self.available_locales:
            locale_name = request.session['lang'] = self.negotiate_locale(request.accept_language)
            request._LOCALE_ = locale_name
        else:
            locale_name = request.session['lang']
            request._LOCALE_ = locale_name
        return locale_name

tsf = TranslationStringFactory('larryslist')
def add_localizer(event):
    request = event.request
    request.set_lang()
    localizer = get_localizer(request)
    def auto_translate(string, mapping = {}):
        return localizer.translate(tsf(string, mapping = mapping))
    request.localizer = localizer
    request._ = request.translate = auto_translate




