from string import Template
import urllib
from babel import Locale
from .i18n import tsf
from pyramid.httpexceptions import HTTPFound
from pyramid.i18n import get_localizer


def fwd_raw(request, location):
    raise HTTPFound(location = location)

def rld_url(request, with_query = True, *args, **kwargs):
    if with_query:
        return request.current_route_url(_query = request.GET, *args, **kwargs)
    else:
        return request.current_route_url(*args, **kwargs)

def rld(request, with_query = True, *args, **kwargs):
    raise HTTPFound(location = request.rld_url(with_query, *args, **kwargs))
def fwd(request, route_name, *args, **kwargs):
    raise HTTPFound(location = request.fwd_url(route_name, *args, **kwargs))

def fwd_url(request, route_name, secure = False, *args, **kwargs):
    if secure:
        return request.route_url(route_name, _scheme = request.globals.secure_scheme, *args, **kwargs)
    else:
        return request.route_url(route_name, _scheme = "http", *args, **kwargs)

def ajax_url(request, route_name, secure = False, escaped = {}, *args, **kwargs):
    tokens = {k:"###{}###".format(k.upper()) for k in escaped}
    params = tokens.copy()
    params.update(kwargs)
    url = request.fwd_url(route_name, secure = secure, *args, **params)
    for key,token in tokens.items():
        url = url.replace(urllib.quote(token), escaped[key])
    return url


def getStaticUrl(request, path):
    if not path or path.startswith("http"):
        return path
    return '//{}{}{}'.format(request.globals.resourceHost, path.strip("/"))

def set_lang(request, lang = None):
    if lang:
        request._LOCALE_ = lang
        request.localizer = None
        request.locale_name = None
    localizer = get_localizer(request)

    def auto_translate(string):
        return localizer.translate(tsf(string))
    def auto_pluralize(singular, plural, n, mapping = {}):
        mapping.update({'num':n})
        try:
            return localizer.pluralize(singular, plural, n, domain='larryslist', mapping=mapping)
        except AttributeError, e:
            if n!=1:
                return Template(plural).substitute(mapping)
            else:
                return Template(singular).substitute(mapping)
    request.localizer = localizer
    request.ungettext = auto_pluralize
    request._ = auto_translate

def getFullLocale(request):
    locales = {'en':'en-GB', 'de':'de-DE', 'es':'es-ES'}
    return locales[request._LOCALE_]
def getLangName(request, langCode = None):
    locale_code = request._LOCALE_
    return Locale.parse(locale_code).languages.get(langCode or locale_code)


def extend_request(config):
    def furl(request):
        return request.params.get("furl") or request.path_qs
    config.add_request_method(furl, 'furl', reify=True)

    def globals(request):
        return request.registry.settings["g"]
    config.add_request_method(globals, 'globals', reify=True)

    def backend(request):
        return request.globals.backend
    config.add_request_method(backend, 'backend', reify=True)

    config.add_request_method(fwd_raw)
    config.add_request_method(rld_url)
    config.add_request_method(rld)
    config.add_request_method(fwd)
    config.add_request_method(fwd_url)
    config.add_request_method(ajax_url)
    config.add_request_method(getStaticUrl)
    config.add_request_method(set_lang)
    config.add_request_method(getFullLocale)
    config.add_request_method(getLangName)


