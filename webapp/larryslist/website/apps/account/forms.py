from jsonclient.backend import DBMessage
import formencode
from larryslist.lib.baseviews import GenericSuccessMessage
from larryslist.lib.formlib.formfields import BaseForm, PasswordField, REQUIRED
from larryslist.website.apps.models import UpdatePasswordProc


class PasswordResetForm(BaseForm):
    id = "pwdreset"
    label = "Password reset"
    action_label = "Save"
    fields = [
        PasswordField("pwd", "New Password", REQUIRED)
        , PasswordField("pwdconfirm", "Confirm New Password", REQUIRED)
    ]
    chained_validators = [formencode.validators.FieldsMatch('pwd', 'pwdconfirm')]
    @classmethod
    def on_success(self, request, values):
        try:
            UpdatePasswordProc(request, {'token':request.root.user.token, 'pwd':values['pwd']})
        except DBMessage:
            raise # HORROR HAPPENED
        request.session.flash(GenericSuccessMessage("Your password has been changed. You can now log in using your new password."), "generic_messages")
        request.fwd("website_user_profile")