from formencode.variabledecode import variable_decode
from larryslist.models.news import GetNewsFeedProc
import simplejson


def index(context, request):
    if context.user.isAnon():
        return {}
    else:
        request.fwd("website_index_member")


def index_member(context, request):
    news = GetNewsFeedProc(request)
    if news:
        news = news.NewsFeed
        if news:
            news = news[:10]
        else: news = []
    else: news = []

    queryMap = variable_decode(request.params)
    query = context.config.convertToQuery(queryMap)
    return {"query": simplejson.dumps(query), 'filters': simplejson.dumps(context.config.getFilterSelection()), 'newsfeed': news}