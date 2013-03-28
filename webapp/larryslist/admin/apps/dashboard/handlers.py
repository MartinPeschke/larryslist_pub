from itertools import ifilter
from operator import methodcaller
from larryslist.admin.apps.dashboard.forms import NewsFeedForm
from larryslist.admin.apps.dashboard.models import GetProfilesProc, GetSubmittedProfiles
from larryslist.lib.formlib.handlers import FormHandler
from larryslist.models.news import GetNewsFeedProc
from pyramid.decorator import reify
from pyramid.renderers import render


def index(context, request):
    return {}
def approvalqueue(context, request):
    if context.user.isAdmin:
        result = GetSubmittedProfiles(request, context.user)
        submitted= ifilter(methodcaller("isSubmitted"), result)
        approved = ifilter(methodcaller("isReviewed"), result)
    else:
        submitted, approved = [], []
    return {"success": True
            , "html": {"submitted":render("larryslist:admin/templates/ajax/approvalqueue.html", {'profiles': submitted}, request).strip()
                     ,  "approved":render("larryslist:admin/templates/ajax/approvalqueue.html", {'profiles': approved}, request).strip()}}

def myprofiles(context, request):
    profiles = GetProfilesProc(request, context.user)
    return {"success": True
            , "html": render("larryslist:admin/templates/ajax/profiles.html", {'profiles': profiles}, request).strip()}



class NewsHandler(FormHandler):
    form = NewsFeedForm

    @reify
    def newsFeed(self):
        return GetNewsFeedProc(self.request)

    def pre_fill_values(self, request, result):
        result['values'][self.form.id] = self.newsFeed.unwrap() or {}
        return result