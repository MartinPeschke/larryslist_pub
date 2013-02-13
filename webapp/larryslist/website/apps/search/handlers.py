import urllib


def index(context, request):
    query = []
    if 'l' in request.params:
        query.append(request.params['l'])
    if 't' in request.params:
        query.append(request.params['t'])
    return {"query": ' '.join(query)}