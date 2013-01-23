import simplejson
from pyramid.response import Response

def wrapJSResponse(result):
    response = Response('define([], function(){{ return {}; }});'.format(simplejson.dumps(result)))
    response.content_type = 'application/javascript'
    response.status_int = 200
    return response
