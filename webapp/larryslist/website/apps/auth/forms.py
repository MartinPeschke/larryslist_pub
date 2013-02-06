from larryslist.lib.formlib.formfields import BaseForm, EmailField, PasswordField, Placeholder

__author__ = 'Martin'



class LoginForm(BaseForm):
    id="login_form"
    fields = [
        EmailField("email", None, attrs = Placeholder("Email"))
        , PasswordField("pwd", None, attrs = Placeholder("Password"))
    ]