


def save(context, request):
    context.cart.setContent(request.json_body)
    return {'success':True}

def index(context, request):
    return {}

def checkout(context, request):
    return {}
