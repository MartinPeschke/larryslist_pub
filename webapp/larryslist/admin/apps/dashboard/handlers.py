from larryslist.admin.apps.dashboard.models import GetProfilesProc, GetSubmittedProfiles


def index(context, request):
    if context.user.isAdmin:
        submitted = GetSubmittedProfiles(request, context.user)
    else:
        submitted = []
    profiles = GetProfilesProc(request, context.user)
    return {"profiles": profiles, "submitted": submitted}
