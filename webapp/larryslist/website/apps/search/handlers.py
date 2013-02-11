import urllib


def index(context, request):
    if 'l' in request.params and 't' in request.params:
        query = u"{l} {t}".format(**request.params)
    else:
        query = ''
    return {"query": query}