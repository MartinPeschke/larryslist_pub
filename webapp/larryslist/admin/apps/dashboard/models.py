from jsonclient import Mapping, TextField, ListField, DictField
from larryslist.admin.apps.collector.models import CollectorModel
from larryslist.models import ClientTokenProc
from larryslist.models.news import NewsFeedModel


_GetProfilesProc = ClientTokenProc("/admin/feeder/collectors", root_key = "Collectors")
def GetProfilesProc(request, user):
    result = _GetProfilesProc(request, {'token':user.token})
    if result:
        return map(CollectorModel.wrap, result.get("Collector", []))
    else:
        return []
_GetSubmittedProfiles = ClientTokenProc("/admin/feeder/submitted", root_key = "Collectors")
def GetSubmittedProfiles(request, user):
    result = _GetSubmittedProfiles(request, {'token':user.token})
    if result:
        return map(CollectorModel.wrap, result.get("Collector", []))
    else:
        return []



SetNewsFeedProc = ClientTokenProc("/admin/feeder/newsfeedset", root_key="NewsFeeds", result_cls=NewsFeedModel)