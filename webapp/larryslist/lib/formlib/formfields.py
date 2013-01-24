from operator import methodcaller, attrgetter
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
        validators = {v.name:v.getValidator(request) for v in cls.fields}
        return formencode.Schema(**validators)


class Field(object):
    template = 'larryslist:lib/formlib/templates/basefield.html'
    validator_args = {'required':False, 'not_empty':False}
    html_help = None
    group_classes = ''
    label_classes = ''
    control_classes = ''
    input_classes = ''
    required = False
    important = False
    def __init__(self, name, label, required = False, classes = '', validator_args = None):
        self.name = name
        self.label = label
        self.required = required
        self.input_classes = '{} {}'.format(self.input_classes, classes)

        self.validator = self._validator(**self.getValidatorArgs(required, validator_args))

    def getValidatorArgs(self, required, args):
        params = self.validator_args.copy()
        if args: params.update(args)
        params['not_empty'] = required
        if not required:
            params['if_missing'] = None
        return params

    def getValidator(self, request):
        return self.validator
    def getLabel(self, request):
        return self.label
    def getName(self, prefix, request):
        return '{}.{}'.format(prefix, self.name)
    def getClasses(self):
        return  '{} {}'.format(self.input_classes, 'required' if self.required else '')
    def render(self, prefix, request, values, errors):
        name = self.name
        if isinstance(errors, formencode.Invalid):
            errors = errors.error_dict
        return render(self.template, {'widget': self, 'prefix':prefix, 'value': values.get(name, ''), 'error':errors.get(name, '')}, request)





class MultipleFormField(Field):
    template = 'larryslist:lib/formlib/templates/repeatableform.html'
    fields = []
    classes = 'form-embedded-wrapper'
    add_more_link_label = 'add'
    def __init__(self, name, label, required = False):
        self.name = name
        self.label = label
        self.required = required

    def getClasses(self):
        return  self.classes

    def getValidator(self, request):
        return formencode.ForEach(formencode.Schema(**{v.name:v.getValidator(request) for v in self.fields}), not_empty = self.required)

    def render(self, prefix, request, values, errors):
        name = self.name
        return render(self.template, {'widget': self, 'prefix':"{}.{}".format(prefix, self.name), 'value': values.get(name, ''), 'error':errors.get(name, '')}, request)



class StringField(Field):
    input_classes = 'input-large'
    _validator = formencode.validators.String


class DateField(StringField):
    input_classes = 'input-large date-field'
    def html_help(self, request):
        return '(yyyy-mm-dd)'
    def __init__(self, name, label, required = False, validator_args = None):
        self.name = name
        self.label = label
        args = self.getValidatorArgs(required, validator_args)
        if 'format' not in args:
            args['format'] = "%Y-%m-%d"
        self.validator = DateValidator(**args)


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








