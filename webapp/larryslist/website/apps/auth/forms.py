import formencode
from larryslist.lib.formlib.formfields import BaseForm, EmailField, PasswordField, Placeholder, REQUIRED, StringField

__author__ = 'Martin'



class LoginForm(BaseForm):
    id="login"
    label ="Login"
    fields = [
        EmailField("email", None, attrs = Placeholder("Email", required = True))
        , PasswordField("pwd", None, attrs = Placeholder("Password", required = True))
    ]

class SignupHandler(BaseForm):
    id="signup"
    label = "Signup"
    fields = [
        StringField("name", "Name", REQUIRED)
        , EmailField("email", "Email", REQUIRED)
        , PasswordField("pwd", "Password", REQUIRED)
        , PasswordField("pwdconfirm", "Confirm password", REQUIRED)
    ]
    chained_validators = [formencode.validators.FieldsMatch('pwd', 'pwdconfirm')]
