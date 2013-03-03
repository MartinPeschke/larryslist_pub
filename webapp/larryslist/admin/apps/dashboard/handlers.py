from larryslist.admin.apps.dashboard.forms import NewsFeedForm
from larryslist.admin.apps.dashboard.models import GetProfilesProc, GetSubmittedProfiles
from larryslist.lib.formlib.handlers import FormHandler
from larryslist.models.news import GetNewsFeedProc
from pyramid.decorator import reify


def index(context, request):
    if context.user.isAdmin:
        submitted = GetSubmittedProfiles(request, context.user)
    else:
        submitted = []
    profiles = GetProfilesProc(request, context.user)
    return {"profiles": profiles, "submitted": submitted}


class NewsHandler(FormHandler):
    form = NewsFeedForm

    @reify
    def newsFeed(self):
        return GetNewsFeedProc(self.request)

    def pre_fill_values(self, request, result):
        result['values'][self.form.id] = self.newsFeed.unwrap()
        return result