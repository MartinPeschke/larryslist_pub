from datetime import datetime
from operator import methodcaller
import formencode
from formencode.validators import OneOf
from larryslist.lib.formlib.validators import DateValidator, TypeAheadValidator
from larryslist.models.config import NullConfigModel
from pyramid.renderers import render
import simplejson


class HtmlAttrs(object):
    classes = ''
    def __init__(self, required = False, important = False, placeholder = ''):
        self.required = required
        self.important = important
        self.placeholder = placeholder

    def getClasses(self):
        classes = self.classes
        if self.required: classes += ' required'
        if self.important: classes += ' important'
        return classes
    def getInputAttrs(self, request):
        attrs = []
        if self.placeholder: attrs.append('placeholder="{}"'.format(self.placeholder))
        return " ".join(attrs)
    def getGroupAttrs(self): return ''
    def getGroupClasses(self): return ''

NONE = HtmlAttrs()
REQUIRED = HtmlAttrs(True)
IMPORTANT = HtmlAttrs(False, True)

class Placeholder(HtmlAttrs):
    def __init__(self, placeholder = '', required = False, important = False):
        self.placeholder = placeholder
        self.required = required
        self.important = important
class DependentAttrs(HtmlAttrs):
    def __init__(self, placeholder, dependency, dependencyValue, required = False, important = False):
        self.placeholder = placeholder
        self.required = required
        self.important = important
        self.dependency = dependency
        self.dependencyValue = dependencyValue
    def getGroupClasses(self): return 'dependent-control'
    def getGroupAttrs(self):
        return 'data-dependency="{}" data-dependency-value="{}"'.format(self.dependency, self.dependencyValue)

class PictureUploadAttrs(HtmlAttrs):
    def __init__(self, singleFile = True, types="jpg,gif,png", required = False, important = False):
        self.singleFile = singleFile
        self.types = types
        self.required = required
        self.important = important
    def getClasses(self): return ''
    def getGroupClasses(self): return 'picture-upload-control'
    def getGroupAttrs(self):
        return 'data-upload-single="{}" data-upload-types="{}"'.format(self.singleFile, self.types)









class BaseSchema(formencode.Schema):
    filter_extra_fields = True
    allow_extra_fields=True


class BaseForm(object):
    id = 'formdata'
    classes = "form-horizontal form-validated"
    fields = []
    extra_forms = []
    pre_validators = []
    chained_validators = []

    @classmethod
    def toFormData(cls, values):
        return values

    template = 'larryslist:lib/formlib/templates/baseform.html'
    def render(self, request):
        return render(self.template, {'form': self}, request)

    @classmethod
    def getSchema(cls, request):
        validators = {}
        for v in cls.fields:
            if v.is_validated:
                validators.update(v.getValidator(request))
        for form in cls.extra_forms:
            validators[form.id] = form.getSchema(request)
        validators['pre_validators'] = cls.pre_validators
        validators['chained_validators'] = cls.chained_validators
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
        return unicode(self.format_string).format(request = request, view = view)
    def render(self, prefix, request, values, errors, view = None):
        return render(self.template, {'widget': self, 'view':view}, request)
    def getClasses(self):
        return self.classes

class PlainHeadingField(BaseField):
    def __init__(self, label, tag = 'h5', classes = ''):
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
    input_classes = 'input-large'
    def __init__(self, name, label, attrs = NONE, classes = '', validator_args = {}, group_classes = '', label_classes = '', input_classes = ''):
        self.name = name
        self.label = label
        self.attrs = attrs
        self.validator_args = validator_args
        self.group_classes = group_classes
        self.label_classes = label_classes
        self.input_classes = input_classes or self.input_classes
        self.input_classes = '{} {}'.format(self.input_classes, classes)


    def getValidatorArgs(self):
        params = self.validator_args.copy()
        if self.validator_args: params.update(self.validator_args)

        params['required'] = self.attrs.required
        params['not_empty'] = self.attrs.required
        if not self.attrs.required:
            params['if_missing'] = None
        return params
    def getValidator(self, request):
        return {self.name: self._validator(**self.getValidatorArgs())}

    def valueToForm(self, value): return value

    def hasLabel(self):
        return bool(self.label)
    def getLabel(self, request):
        return self.label
    def getName(self, prefix):
        return '{}.{}'.format(prefix, self.name)
    def getClasses(self):
        return  '{} {}'.format(self.input_classes, self.attrs.getClasses())

    def getValues(self, name, request, values, errors, view):
        return {'value': values.get(name, ''), 'error':errors.get(name, '')}
    def render(self, prefix, request, values, errors, view = None):
        if isinstance(errors, formencode.Invalid):
            errors = errors.error_dict
        params = self.getValues(self.name, request, values, errors, view)
        params.update({'widget': self, 'prefix':prefix, 'view': view})
        return render(self.template, params, request)


class MultipleFormField(Field):
    template = 'larryslist:lib/formlib/templates/repeatableform.html'
    fields = []
    add_more_link_label = '+'
    def __init__(self, name, label = None, attrs = NONE, classes = 'form-embedded-wrapper'):
        self.name = name
        self.label = label
        self.attrs = attrs
        self.classes = classes

    def getClasses(self):
        return  self.classes

    def getValidator(self, request):
        validators = {}
        for v in self.fields:
            if v.is_validated:
                validators.update(v.getValidator(request))
        return {self.name : formencode.ForEach(BaseSchema(**validators), not_empty = self.attrs.required)}

    def render(self, prefix, request, values, errors, view = None):
        name = self.name
        return render(self.template, {'widget': self, 'prefix':"{}.{}".format(prefix, self.name), 'value': values.get(name, ''), 'error':errors.get(name, ''), 'view':view}, request)











class StaticHiddenField(Field):
    _validator = formencode.validators.String
    def __init__(self, name, value):
        self.name = name
        self.value = value
    def render(self, prefix, request, values, errors, view = None):
        return '<input type="hidden" name="{}" value="{}"/>'.format(self.getName(prefix), self.value)

class HiddenField(Field):
    _validator = formencode.validators.String
    def render(self, prefix, request, values, errors, view = None):
        return '<input type="hidden" name="{}" value="{}"/>'.format(self.getName(prefix), values.get(self.name, ''))

    def __init__(self, name):
        self.name = name


class StringField(Field):
    _validator = formencode.validators.String
class IntField(Field):
    input_classes = 'input-mini digits'
    _validator = formencode.validators.Int
class URLField(Field):
    input_classes = 'input-xxlarge'
    _validator = formencode.validators.URL
class EmailField(StringField):
    input_classes = 'input-large email'
    type = 'email'
    validator_args = {'resolve_domain': True}
    _validator = formencode.validators.Email
class PasswordField(StringField):
    input_classes = 'input-large'
    type = 'password'
    validator_args = {'min': 6}
    _validator = formencode.validators.String
class PictureUploadField(StringField):
    template = 'larryslist:lib/formlib/templates/picture_upload.html'
    group_classes = "widget-plupload"
    type = 'hidden'
    _validator = formencode.validators.String


class ApproxField(Field):
    template = 'larryslist:lib/formlib/templates/approx_field.html'
    input_classes = 'input-large digits'
    _validator = formencode.validators.Int
    aprxDefault = 'true'
    type = 'text'
    aprxLabel = "More than"
    def __init__(self, name, aprxName, label, attrs = NONE, classes = '', validator_args = {}, group_classes = '', label_classes = ''):
        super(ApproxField, self).__init__(name, label, attrs, classes, validator_args, group_classes, label_classes)
        self.aprxName = aprxName
    def getName(self, prefix = None, aprx = False):
        return '{}.{}'.format(prefix, self.aprxName if aprx else self.name)
    def getValues(self, name, request, values, errors, view):
        return {'value': values.get(name, ''), 'valueIsApprox':values.get(self.aprxName, False), 'error':errors.get(name, {})}
    def getValidator(self, request):
        result = {}
        result[self.name] = formencode.validators.Int()
        result[self.aprxName] = formencode.validators.StringBool(if_missing = False)
        return result

class CheckboxField(Field):
    template = 'larryslist:lib/formlib/templates/checkbox.html'
    input_classes = 'checkbox'
    value = 'true'
    validator_args = {'if_missing': False}
    _validator = formencode.validators.StringBool
class RadioBoolField(CheckboxField):
    template = 'larryslist:lib/formlib/templates/radiobool.html'
    input_classes = 'radio'




class DateField(StringField):
    input_classes = 'input-large date-field'
    format = "%Y-%m-%d"
    def html_help(self, request):
        return '(yyyy-mm-dd)'
    def __init__(self, name, label, attrs = NONE, validator_args = {}):
        self.name = name
        self.label = label
        self.attrs = attrs
        self.validator_args = validator_args

    def valueToForm(self, value):
        return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S").strftime(self.format) if value else ''




class ChoiceField(Field):
    template = 'larryslist:lib/formlib/templates/dropdown.html'
    def __init__(self, name, label, optionGetter, attrs = NONE):
        self.name = name
        self.label = label
        self.attrs = attrs
        self.optionGetter = optionGetter

    def getValidator(self, request):
        return {self.name: OneOf(map(methodcaller('getKey', request), self.optionGetter(request)), hideList = True)}
    def getOptions(self, request):
        return self.optionGetter(request)
    def isSelected(self, option, value, request):
        return option.getKey(request) == value

def configattr(name, default_none):
    def f(request):
        values = getattr(request.context.config, name)
        if default_none:
            values = [NullConfigModel()] + list(values)
        return values
    return f
class ConfigChoiceField(ChoiceField):
    def __init__(self, name, label, configAttr, attrs = NONE, default_none = True):
        self.name = name
        self.label = label
        self.attrs = attrs
        self.optionGetter = configattr(configAttr, default_none)


class TypeAheadField(StringField):
    template = 'larryslist:lib/formlib/templates/typeahead.html'
    def __init__(self, name, label, api_url, api_result, dependency = None, attrs = NONE, classes = 'typeahead', validator_args = {}):
        super(TypeAheadField, self).__init__(name, label, attrs, classes, validator_args)
        self.dependency = dependency
        self.api_result = api_result
        self.api_type = None
        self.api_url = api_url

    def getValues(self, name, request, values, errors, view):
        return {'value': values.get(name, ''), 'error':errors.get(name, '')}

class TagSearchField(StringField):
    template = 'larryslist:lib/formlib/templates/tagsearch.html'
    def __init__(self, name, label, api_url, api_result, api_allow_new = True, attrs = NONE, classes = 'tagsearch', validator_args = {}):
        super(TagSearchField, self).__init__(name, label, attrs, classes, validator_args)
        self.api_result = api_result
        self.api_allow_new = api_allow_new
        self.api_type = None
        self.api_url = api_url

    def getValidator(self, request):
        return {self.name: formencode.ForEach(name = formencode.validators.String(required=True))}
    def getValueData(self, name, request, value):
        return simplejson.dumps(value)



class TokenTypeAheadField(StringField):
    template = 'larryslist:lib/formlib/templates/typeahead_token.html'
    def __init__(self, name, label, api_url, api_result, dependency = None, attrs = NONE, classes = 'typeahead', validator_args = {}):
        super(TokenTypeAheadField, self).__init__(name, label, attrs, classes, validator_args)
        self.dependency = dependency
        self.api_result = api_result
        self.api_url = api_url

    def getValidator(self, request):
        return {self.name: TypeAheadValidator(self.attrs)}

    def getValues(self, name, request, values, errors, view):
        return {'value': values.get(name, {}), 'error':errors.get(name, {})}







# =========================== COMPOUNDS

def MultiConfigChoiceField(name, label, configKey, *args, **kwargs):
    class cls(MultipleFormField):
        fields = [
            ConfigChoiceField(name, label, configKey)
        ]
    return cls(*args, **kwargs)