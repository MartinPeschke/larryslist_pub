from xml.sax.saxutils import quoteattr
from formencode.variabledecode import variable_decode
import simplejson


def index(context, request):
    query = variable_decode(request.params)
    return {"query": quoteattr(simplejson.dumps(query))}