from larryslist.admin.apps.settings.forms import FeederCreateForm
from larryslist.lib.formlib.handlers import FormHandler


class FeederHandler(FormHandler):
    forms = [FeederCreateForm]