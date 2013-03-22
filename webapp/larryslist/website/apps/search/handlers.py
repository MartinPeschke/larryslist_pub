from xml.sax.saxutils import quoteattr
from formencode.variabledecode import variable_decode
import simplejson


def index(context, request):
    queryMap = variable_decode(request.params)
    query = context.config.convertToQuery(queryMap)
    return {"query": simplejson.dumps(query), 'filters': simplejson.dumps(context.config.getFilterSelection())}


def entities(context, request):
    return context.config.querySearch(request.json_body)