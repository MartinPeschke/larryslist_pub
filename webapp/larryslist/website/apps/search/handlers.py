from xml.sax.saxutils import quoteattr
from formencode.variabledecode import variable_decode
import simplejson


def index(context, request):
    query = variable_decode(request.params)
    query = query.get("q", [])
    return {"query": simplejson.dumps(query)}