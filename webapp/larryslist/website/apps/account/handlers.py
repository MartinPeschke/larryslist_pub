from larryslist.lib.formlib.handlers import FormHandler
from .forms import PasswordResetForm
from larryslist.website.apps.models import RefreshUserProfileProc


class ProfileHandler(FormHandler):
    form = PasswordResetForm

    def GET(self):
        request = self.request
        RefreshUserProfileProc(request, {'token':request.root.user.token})
        return super(ProfileHandler, self).GET()
