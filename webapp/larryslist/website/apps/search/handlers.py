from xml.sax.saxutils import quoteattr
from formencode.variabledecode import variable_decode
import simplejson


def index(context, request):
    queryMap = variable_decode(request.params)
    query = context.config.convertToQuery(queryMap)
    return {"query": simplejson.dumps(query), 'filters': simplejson.dumps(context.config.getFilterSelection())}


def entities(context, request):
    return request.globals.typeahead_search.get(request.json_body['key'], request.json_body['value'])

def entities_more(context, request):
    term = request.matchdict.get("term")
    offset= int(request.matchdict.get("offset"))
    return context.config.getMore(term, offset, 100)