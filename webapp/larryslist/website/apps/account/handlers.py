from larryslist.lib.formlib.handlers import FormHandler
from .forms import PasswordResetForm


class ProfileHandler(FormHandler):
    form = PasswordResetForm