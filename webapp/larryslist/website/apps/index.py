from larryslist.models.news import GetNewsFeedProc


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
    return {'query':'', 'newsfeed': news}