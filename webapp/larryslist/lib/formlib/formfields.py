from operator import methodcaller
import formencode
from formencode.validators import OneOf
from larryslist.lib.formlib.validators import DateValidator
from pyramid.renderers import render



REQUIRED = True


class BaseForm(object):
    id = 'formdata'
    fields = []

    template = 'larryslist:lib/formlib/templates/baseform.html'
    def render(self, request):
        return render(self.template, {'form': self}, request)

    @classmethod
    def getSchema(cls, request):
        validators = {v.name:v.getValidator(request)  for v in cls.fields}
        return formencode.Schema(**validators)



class Field(object):
    template = 'larryslist:lib/formlib/templates/basefield.html'
    html_help = None
    group_classes = ''
    label_classes = ''
    control_classes = ''
    input_classes = ''
    required = False
    important = False

    def getValidator(self, request):
        return self.validator
    def getLabel(self, request):
        return self.label
    def getName(self, request, prefix = None):
        if prefix:
            return '{}.{}'.format(prefix, self.name)
        else:
            return self.name
    def render(self, form, request, values, errors):
        name = self.getName(request)
        return render(self.template, {'widget': self, 'form':form, 'value': values.get(name, ''), 'error':errors.get(name, '')}, request)



class StringField(Field):
    validator_args = {'required':True, 'not_empty':True, 'min':2}
    input_classes = 'input-large'
    def __init__(self, name, label, required = False, classes = '', validator_args = None):
        self.name = name
        self.label = label
        self.required = required
        self.input_classes = '{} {}'.format(self.input_classes, classes)

        params = (validator_args or self.validator_args)
        params['required'] = required
        self.validator = formencode.validators.String(**params)


class DateField(StringField):
    def html_help(self, request):
        return '(yyyy-mm-dd)'
    def __init__(self, name, label, required = False, validator_args = None):
        self.name = name
        self.label = label
        params = (validator_args or self.validator_args)
        params['required'] = required
        if 'format' not in params:
            params['format'] = "%Y-%m-%d"
        self.validator = DateValidator(**params)


def configattr(name):
    def f(request):
        return getattr(request.context.config, name)
    return f


class ChoiceField(Field):
    template = 'larryslist:lib/formlib/templates/dropdown.html'
    def __init__(self, name, label, optionGetter):
        self.name = name
        self.label = label
        self.optionGetter = optionGetter

    def getValidator(self, request):
        return OneOf(map(methodcaller('getKey', request), self.optionGetter(request)))
    def getOptions(self, request):
        return self.optionGetter(request)
    def isSelected(self, option, value, request):
        return option.getKey(request) == value

class ConfigChoiceField(ChoiceField):
    def __init__(self, name):
        self.name = name
        self.label = name
        self.optionGetter = configattr(name)