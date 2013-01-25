from datetime import datetime
from operator import methodcaller
import formencode
from formencode.validators import OneOf
from larryslist.lib.formlib.validators import DateValidator, TypeAheadValidator
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



class BaseSchema(formencode.Schema):
    filter_extra_fields = True
    allow_extra_fields=True


class BaseForm(object):
    id = 'formdata'
    classes = "form-horizontal form-validated"
    fields = []

    @classmethod
    def toFormData(cls, values):
        return values

    template = 'larryslist:lib/formlib/templates/baseform.html'
    def render(self, request):
        return render(self.template, {'form': self}, request)

    @classmethod
    def getSchema(cls, request):
        validators = {v.name:v.getValidator(request) for v in cls.fields if v.is_validated}
        return BaseSchema(**validators)

class BaseField(object):
    is_validated = False
    html_help = None
    group_classes = ''
    label_classes = ''
    control_classes = ''
    input_classes = ''
    attrs = NONE



class HeadingField(BaseField):
    tag = 'legend'
    template = 'larryslist:lib/formlib/templates/heading.html'
    def __init__(self, format_string, classes = ''):
        self.format_string = format_string
        self.classes = classes
    def getHeading(self, request, view):
        return self.format_string.format(request = request, view = view)
    def render(self, prefix, request, values, errors, view = None):
        return render(self.template, {'widget': self, 'view':view}, request)
    def getClasses(self):
        return self.classes

class PlainHeadingField(BaseField):
    def __init__(self, label, tag = 'h4', classes = ''):
        self.label = label
        self.tag = tag
        self.classes = classes
    def render(self, prefix, request, values, errors, view = None):
        return '<{0.tag} class="{0.classes}">{0.label}</{0.tag}>'.format(self)



class Field(BaseField):
    template = 'larryslist:lib/formlib/templates/basefield.html'
    is_validated = True
    validator_args = {}
    type = 'text'
    def __init__(self, name, label, attrs = NONE, classes = '', validator_args = None, group_classes = '', label_classes = ''):
        self.name = name
        self.label = label
        self.attrs = attrs
        self.group_classes = group_classes
        self.label_classes = label_classes
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

    def convertValue(self, value): return value

    def getValidator(self, request):
        return self.validator
    def hasLabel(self):
        return bool(self.label)
    def getLabel(self, request):
        return self.label
    def getName(self, prefix):
        return '{}.{}'.format(prefix, self.name)
    def getClasses(self):
        return  '{} {}'.format(self.input_classes, self.attrs.getClasses())
    def render(self, prefix, request, values, errors, view = None):
        name = self.name
        if isinstance(errors, formencode.Invalid):
            errors = errors.error_dict
        return render(self.template, {'widget': self, 'prefix':prefix, 'value': values.get(name, ''), 'error':errors.get(name, ''), 'view': view}, request)


class StaticHiddenField(Field):
    input_classes = 'input-large'
    def __init__(self, name, value):
        self.name = name
        self.value = value
        self.validator = formencode.validators.String
    def render(self, prefix, request, values, errors, view = None):
        return '<input type="hidden" name="{}" value="{}"/>'.format(self.getName(prefix), self.value)

class HiddenField(Field):
    input_classes = 'input-large'
    _validator = formencode.validators.String
    def render(self, prefix, request, values, errors, view = None):
        return '<input type="hidden" name="{}" value="{}"/>'.format(self.getName(prefix), values.get(self.name, ''))



class StringField(Field):
    input_classes = 'input-large'
    _validator = formencode.validators.String
class IntField(Field):
    input_classes = 'input-large digits'
    _validator = formencode.validators.Int
class CheckboxField(Field):
    template = 'larryslist:lib/formlib/templates/checkbox.html'
    input_classes = 'checkbox'
    value = 'true'
    _validator = formencode.validators.StringBool

class URLField(Field):
    input_classes = 'input-xlarge'
    _validator = formencode.validators.URL
class EmailField(StringField):
    input_classes = 'input-large email'
    type = 'email'
    validator_args = {'resolve_domain': True}
    _validator = formencode.validators.Email

class DateField(StringField):
    input_classes = 'input-large date-field'
    format = "%Y-%m-%d"
    def html_help(self, request):
        return '(yyyy-mm-dd)'
    def __init__(self, name, label, attrs = NONE, validator_args = None):
        self.name = name
        self.label = label
        self.attrs = attrs
        args = self.getValidatorArgs(attrs, validator_args)
        if 'format' not in args:
            args['format'] = self.format
        self.validator = DateValidator(**args)

    def convertValue(self, value):
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").strftime(self.format) if value else ''

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
    def __init__(self, name, label, configAttr, attrs = NONE):
        self.name = name
        self.label = label
        self.attrs = attrs
        self.optionGetter = configattr(configAttr)


class MultipleFormField(Field):
    template = 'larryslist:lib/formlib/templates/repeatableform.html'
    fields = []
    add_more_link_label = 'add'
    def __init__(self, name, label = None, attrs = NONE, classes = 'form-embedded-wrapper'):
        self.name = name
        self.label = label
        self.attrs = attrs
        self.classes = classes

    def getClasses(self):
        return  self.classes

    def getValidator(self, request):
        return formencode.ForEach(BaseSchema(**{v.name:v.getValidator(request) for v in self.fields if v.is_validated}), not_empty = self.attrs.required)

    def render(self, prefix, request, values, errors, view = None):
        name = self.name
        return render(self.template, {'widget': self, 'prefix':"{}.{}".format(prefix, self.name), 'value': values.get(name, ''), 'error':errors.get(name, ''), 'view':view}, request)





class TypeAheadField(StringField):
    template = 'larryslist:lib/formlib/templates/typeahead.html'
    def __init__(self, name, label, api_url, dependency = None, attrs = NONE, classes = 'typeahead', validator_args = None):
        super(TypeAheadField, self).__init__(name, label, attrs, classes, validator_args)
        self.dependency = dependency
        self.api_url = api_url

    def getValidator(self, request):
        return TypeAheadValidator(self.attrs)
    def render(self, prefix, request, values, errors, view = None):
        name = self.name
        if isinstance(errors, formencode.Invalid):
            errors = errors.error_dict
        return render(self.template, {'widget': self, 'prefix':prefix, 'value': values.get(name, {}), 'error':errors.get(name, ''), 'view': view}, request)







# =========================== COMPOUNDS

def MultiConfigChoiceField(name, label, configKey, *args, **kwargs):
    class cls(MultipleFormField):
        fields = [
            ConfigChoiceField(name, label, configKey)
        ]
    return cls(*args, **kwargs)