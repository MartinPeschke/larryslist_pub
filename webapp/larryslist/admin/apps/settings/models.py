from jsonclient import DictField, ListField, Mapping
from larryslist.admin.apps.auth.models import AdminUser
from larryslist.models import ClientTokenProc


class FeedersModel(Mapping):
    Feeder = ListField(DictField(AdminUser))

CreateUserProc = ClientTokenProc("/admin/feeder/create")

_GetAllUsersProc = ClientTokenProc("/admin/feeder/list", root_key='Feeders', result_cls=FeedersModel)
def GetAllUsersProc(request):
    result = _GetAllUsersProc(request)
    return result.Feeder
