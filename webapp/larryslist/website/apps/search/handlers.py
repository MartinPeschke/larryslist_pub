import urllib


def index(context, request):
    search = request.params.copy()
    if len(search.keys()):
        request.fwd('website_search', query = " ".join(filter(None, search.values())))
    return {"search":search, "query": urllib.unquote_plus(request.matchdict['query'])}