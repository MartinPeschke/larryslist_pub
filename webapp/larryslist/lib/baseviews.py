from pyramid.httpexceptions import HTTPFound
import simplejson
import formencode
from pyramid.decorator import reify

class GenericMessage(object):
    types = ['success', 'info', 'block', 'error', 'danger']
    def __init__(self, body, heading= None):
        self.heading = heading
        self.body= body
class GenericSuccessMessage(GenericMessage):
    type = 'success'
class GenericInfoMessage(GenericMessage):
    type = 'info'
class GenericBlockMessage(GenericMessage):
    type = 'block'
class GenericErrorMessage(GenericMessage):
    type = 'error'
class GenericDangerMessage(GenericMessage):
    type = 'danger'


class BaseHandler(object):
    def __init__(self, context, request):
        self.request = request
        self.context = context

class RootContext(object):
    app_label = 'root'
    root_statics = '/static/'
    static_prefix = '/static/'
    def __init__(self, request):
        self.request = request
        self.backend = request.backend

    def is_allowed(self, request):
        return True

    @reify
    def settings(self):
        return getattr(self.request.globals, self.app_label)