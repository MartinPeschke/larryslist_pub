from .baseviews import RootContext

def context_authorization(event):
    request = event.request
    if isinstance(request.root, RootContext):
        request.root.is_allowed(request)


class TemplateApi(object):
    def __init__(self, request, app_label):
        if getattr(request, 'template_api', None) is None:
            request.template_api = self


def add_renderer_variables(event):
    if event['renderer_name'] != 'json':
        request = event['request']
        app_globals = request.globals
        event.update({"g"       : app_globals
            , 'vctxt'           : request.root
            , '_'               : request.translate
            , 'ungettext'       : request.ungettext
            , 'ROOT_STATIC_URL' : request.root.root_statics
            , 'STATIC_URL'      : request.root.static_prefix
            , 'VERSION_TOKEN'   : app_globals.VERSION_TOKEN
        })

        api = getattr(request, 'template_api', None)
        if api is None and request is not None:
            event['API'] = TemplateApi(request, request.root.app_label)
    return event