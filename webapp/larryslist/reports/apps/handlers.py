__author__ = 'Martin'


def reports(context, request):
    slug = request.matchdict['slug']
    return {'report' : context.settings.reportMap[slug]}

def user_actions(context, request):
    return {}