from jsonclient.backend import AuthenticatedRemoteProc, RemoteProc, DBException

__author__ = 'Martin'


def ClientTokenProc(path, root_key = None, result_cls = None, method = "POST", result_list = False):
    def auth_extractor(request):
        return {'Client-Token':request.root.client_token}
    return AuthenticatedRemoteProc(path, method, auth_extractor, root_key, result_cls, result_list)



class MetaRemoteProc(RemoteProc):
    def __init__(self, remote_path, auth_extractor):
        super(MetaRemoteProc, self).__init__(remote_path, "POST", 'json')
        self.auth_extractor = auth_extractor
    def __call__(self, request, id, data = {}):
        backend = request.backend
        result = self.call(backend, data, headers = self.auth_extractor(request, id, data))
        return result if result else {}
def MetaDataProc(path):
    def auth_extractor(request, id, data = {}):
        return {'Client-Token':request.root.client_token, 'JsonObjectId':id}
    return MetaRemoteProc(path, auth_extractor)



def wrap_proc_token(proc):
    def f(request, data = {}):
        data['token'] = request.user.token
        return proc(request, data)
    return f

def getRecItem(keys, map, default = []):
    for key in keys.split("."):
        map = map.get(key, {})
        if not map: return default
    return map


def LocalizedListProc(proc, key, obj):
    def f(request, data = {}):
        data['lang'] = request._LOCALE_
        result = proc(request, data)
        result = map(obj.wrap, result.get(key+"s", {}).get(key, []))
        return result
    return f

