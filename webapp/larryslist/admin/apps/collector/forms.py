from larryslist.lib.formlib.formfields import REQUIRED, StringField, BaseForm

__author__ = 'Martin'




class CreateHandlerForm(BaseForm):
    classes = "form-horizontal form-validated"
    fields = [
        StringField('firstName', 'First Name', REQUIRED)
        , StringField('lastName', 'Last Name', REQUIRED)
        , StringField('originalName', 'Name in orig. Language')
    ]