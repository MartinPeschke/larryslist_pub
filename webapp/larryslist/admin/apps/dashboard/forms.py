from larryslist.admin.apps.dashboard.models import SetNewsFeedProc
from larryslist.lib.formlib.formfields import BaseForm, MultipleFormField, StringField, TextareaField, HiddenField


class NewsItemForm(MultipleFormField):
    fields = [
        TextareaField("value", "Text", input_classes="span8 input-xxlarge")
        , StringField("source", "Source", input_classes="span8")
        , HiddenField("created")
    ]

class NewsFeedForm(BaseForm):
    fields = [NewsItemForm("NewsFeed")]

    @classmethod
    def on_success(cls, request, values):
        SetNewsFeedProc(request, values)
        return {'success':True, 'redirect':request.url}
