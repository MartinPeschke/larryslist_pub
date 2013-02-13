import urllib


def index(context, request):
    query = ''
    if 'l' in request.params:
        query += request.params['l']
    if 't' in request.params:
        query += request.params['t']
    return {"query": query}