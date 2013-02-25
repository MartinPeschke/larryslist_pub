import urllib


def index(context, request):
    query = [v for k,v in request.params.items() if k in ['l', 't'] and v]
    return {"query": ' '.join(query)}