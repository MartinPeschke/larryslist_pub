from larryslist.models.news import GetNewsFeedProc


def index(context, request):
    if context.user.isAnon():
        return {}
    else:
        request.fwd("website_index_member")


def index_member(context, request):
    return {'query':'', 'newsfeed': GetNewsFeedProc(request).NewsFeed[:10]}