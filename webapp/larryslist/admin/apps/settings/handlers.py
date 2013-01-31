from larryslist.admin.apps.settings.forms import FeederCreateForm
from larryslist.admin.apps.settings.models import GetAllUsersProc
from larryslist.lib.formlib.handlers import FormHandler


class FeederHandler(FormHandler):
    forms = [FeederCreateForm]


    def pre_fill_values(self, request, result):
        result['feeders'] = GetAllUsersProc(request)
        return result