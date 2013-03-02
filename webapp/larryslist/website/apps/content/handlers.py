def index(context, request):
    return {'static_root': '{}content/'.format(request.root.static_prefix)}
