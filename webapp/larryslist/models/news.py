from jsonclient import Mapping, TextField, ListField, DictField, DateTimeField
from larryslist.models import ClientTokenProc


class NewsItemModel(Mapping):
    source = TextField()
    value = TextField()
    created = DateTimeField()
class NewsFeedModel(Mapping):
    NewsFeed = ListField(DictField(NewsItemModel))

GetNewsFeedProc = ClientTokenProc("/admin/feeder/newsfeed", root_key="NewsFeeds", result_cls=NewsFeedModel)
