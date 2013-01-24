from collections import namedtuple
from operator import methodcaller, attrgetter
import formencode
from formencode.validators import OneOf
from larryslist.lib.formlib.validators import DateValidator
from pyramid.renderers import render

class HtmlAttrs(object):
    def __init__(self, required = False, important = False):
        self.required = required
        self.important = important

    def getClasses(self):
        classes = []
        if self.required: classes.append('required')
        if self.important: classes.append('important')
        return ' '.join(classes)

NONE = HtmlAttrs()
REQUIRED = HtmlAttrs(True)
IMPORTANT = HtmlAttrs(False, True)




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
    validator_args = {}
    html_help = None
    group_classes = ''
    label_classes = ''
    control_classes = ''
    input_classes = ''
    attrs = NONE
    def __init__(self, name, label, attrs = NONE, classes = '', validator_args = None):
        self.name = name
        self.label = label
        self.attrs = attrs
        self.input_classes = '{} {}'.format(self.input_classes, classes)

        self.validator = self._validator(**self.getValidatorArgs(attrs, validator_args))

    def getValidatorArgs(self, attrs, args):
        params = self.validator_args.copy()
        if args: params.update(args)

        params['required'] = attrs.required
        params['not_empty'] = attrs.required
        if not attrs.required:
            params['if_missing'] = None
        return params

    def getValidator(self, request):
        return self.validator
    def getLabel(self, request):
        return self.label
    def getName(self, prefix, request):
        return '{}.{}'.format(prefix, self.name)
    def getClasses(self):
        return  '{} {}'.format(self.input_classes, self.attrs.getClasses())
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
    def __init__(self, name, label, attrs = NONE):
        self.name = name
        self.label = label
        self.attrs = attrs

    def getClasses(self):
        return  self.classes

    def getValidator(self, request):
        return formencode.ForEach(formencode.Schema(**{v.name:v.getValidator(request) for v in self.fields}), not_empty = self.attrs.required)

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
    def __init__(self, name, label, attrs = NONE, validator_args = None):
        self.name = name
        self.label = label
        self.attrs = attrs
        args = self.getValidatorArgs(attrs, validator_args)
        if 'format' not in args:
            args['format'] = "%Y-%m-%d"
        self.validator = DateValidator(**args)


def configattr(name):
    def f(request):
        return getattr(request.context.config, name)
    return f


class ChoiceField(Field):
    template = 'larryslist:lib/formlib/templates/dropdown.html'
    def __init__(self, name, label, optionGetter, attrs = NONE):
        self.name = name
        self.label = label
        self.attrs = attrs
        self.optionGetter = optionGetter

    def getValidator(self, request):
        return OneOf(map(methodcaller('getKey', request), self.optionGetter(request)))
    def getOptions(self, request):
        return self.optionGetter(request)
    def isSelected(self, option, value, request):
        return option.getKey(request) == value

class ConfigChoiceField(ChoiceField):
    def __init__(self, name, attrs = NONE):
        self.name = name
        self.label = name
        self.attrs = attrs
        self.optionGetter = configattr(name)








