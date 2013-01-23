import formencode
from pyramid.renderers import render



REQUIRED = True


class BaseForm(object):
    id = 'formdata'
    validators = []

    template = 'larryslist:lib/formlib/templates/baseform.html'
    def render(self, request):
        return render(self.template, {'form': self}, request)


class Field(object):
    template = 'larryslist:lib/formlib/templates/basefield.html'

    group_classes = ''
    label_classes = ''
    control_classes = ''
    input_classes = ''


    def getLabel(self, request):
        return self.label
    def getName(self, request):
        return self.name
    def render(self, request):
        return render(self.template, {'widget': self}, request)





class StringField(Field):
    validator_args = {'required':True, 'not_empty':True, 'min':2}
    def __init__(self, name, label, required = False, validator_args = None):
        self.name = name
        self.label = label

        params = (validator_args or self.validator_args)
        params['required'] = required
        self.validator = formencode.validators.String(**params)
