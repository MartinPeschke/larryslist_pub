from formencode.validators import Invalid
from BeautifulSoup import BeautifulSoup
import formencode
from datetime import datetime
from babel.numbers import parse_decimal, format_decimal, NumberFormatError
from operator import methodcaller

import logging
log = logging.getLogger(__name__)



_ = lambda s: s


class FormHeading(object):
    structure = "heading"
    def __init__(self, html_label, tag = 'legend', classes = '', field_names = None):
        self.html_label = html_label
        self.tag = tag
        self.classes = classes
        if isinstance(field_names, basestring):
            self.field_names = {field_names:field_names}
        elif isinstance(field_names, list):
            self.field_names = {name:name for name in field_names}
        else:
            self.field_names = field_names

    def getLabel(self, values):
        if self.field_names:
            return self.html_label.format(**{k:values.get(v) for k,v in self.field_names.items()})
        else:
            return self.html_label

class FormSection(object):
  structure = "layout"
  def __init__(self, form_order, tag = 'div', classes = 'view-set'):
    self.tag = tag
    self.classes = classes
    self.form_order = form_order
  
class CustomFormElement(object):
  structure = "widget"
  def __init__(self, widget):
    self.widget = widget
  
class CombinedElement(object):
    structure = "combined"
    suppress_label = False
    inline_label = True
    def __init__(self, elements, html_label = None, **kwargs):
        self.html_label = html_label
        self.elements = elements
        for k,v in kwargs.items():
            setattr(self, k, v)

    def showOutsideLabel(self):
        return not (self.suppress_label or self.inline_label)
    def getFields(self, schema):
        return [schema.fields[field] for field in self.elements]
    def getErrors(self, errors):
        return filter(None, [errors.get(f) for f in self.elements])
    def required(self, schema):
        return len(filter(None, [getattr(f, "required", None) for f in self.getFields(schema)])) > 0

class SanitizedHTMLString(formencode.validators.String):
  messages = {"invalid_format":'There was some error in your HTML!'}
  valid_tags = ['a','strong', 'em', 'p', 'ul', 'ol', 'li', 'br', 'b', 'i', 'u', 's', 'strike', 'font', 'pre', 'blockquote', 'div', 'span', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6']
  valid_attrs = ['size', 'color', 'face', 'title', 'align', "style"]

  def linkAttrs(self, attrs):
    return [('href', attrs.get('href')), ('target', '_blank')]

  def sanitize_html(self, html):
      soup = BeautifulSoup(html)
      for tag in soup.findAll(True):
          if tag.name.lower() not in self.valid_tags:
              tag.extract()
          elif tag.name.lower() != "a":
              tag.attrs = [attr for attr in tag.attrs if attr[0].lower() in self.valid_attrs]
          else:
              attrs = dict(tag.attrs)
              tag.attrs = self.linkAttrs(attrs)
      val = soup.renderContents()
      return val.decode("utf-8")
  def _to_python(self, value, state):
    value = super(SanitizedHTMLString, self)._to_python(value, state)
    try:
      return self.sanitize_html(value)
    except Exception, e:
      log.error("HTML_SANITIZING_ERROR %s", value)
      raise formencode.Invalid(self.message("invalid_format", state, value = value), value, state)

class Choice(object):
    def __init__(self, key, label, **kwargs):
        self.label = label
        self.key = key
        for k,v in kwargs.items():
            setattr(self, k, v)

    def getKey(self, state = None):
        return self.key
    def getValue(self, state = None):
        return self.label
    getLabel = getValue
      
class OneOfChoice(formencode.validators.OneOf):
    custom_attribute = 'custom'
    tabindex=5
    def keyToPython(self, value, state = None):
        return value
    
    def getKeys(self, state):
        return map(methodcaller("getKey", state), self.getItems(state))
    def getValues(self, state):
        return map(methodcaller("getValue", state), self.getItems(state))
    def getItems(self, state):
      return self.choices
    
    def _to_python(self, value, state):
        val = self.keyToPython(value, state)
        self.list = self.getKeys(state)
        if not val in self.list:
            if self.hideList:
                raise Invalid(self.message('invalid', state), val, state)
            else:
                try:
                    items = '; '.join(map(str, self.list))
                except UnicodeError:
                    items = '; '.join(map(unicode, self.list))
                raise Invalid(
                    self.message('notIn', state,
                        items=items, val=val), val, state)
        return val
    validate_python = formencode.FancyValidator._validate_noop
    
class OneOfChoiceInt(OneOfChoice):
    def keyToPython(self, value, state):
        if value is None: return None
        try:
            return int(value)
        except:
            raise Invalid(self.message('invalid', state), value, state)

class OneOfStateChoice(OneOfChoice):
    def getItems(self, request):
      obj = request
      for key in self.stateKey.split("."): obj = getattr(obj, key)
      return obj

class ManyOfStateChoice(OneOfChoice):
    def getItems(self, request):
        obj = request
        for key in self.stateKey.split("."): obj = getattr(obj, key)
        return obj
    def _to_python(self, value, state):
        if not isinstance(value, list): value = [value]
        values = [self.keyToPython(v, state) for v in value]
        self.list = self.getKeys(state)
        if len(set(values).difference(self.list)):
            if self.hideList:
                raise Invalid(self.message('invalid', state), values, state)
            else:
                try:
                    items = '; '.join(map(str, self.list))
                except UnicodeError:
                    items = '; '.join(map(unicode, self.list))
                raise Invalid(
                    self.message('notIn', state,
                        items=items, val=values), val, state)
        return values
    
class OneOfState(formencode.validators.OneOf):
    isChoice = True
    list = None
    stateKey = None
    testValueList = False
    hideList = False
    getValue = None
    getKey = None
    custom_attribute = 'custom'
    __unpackargs__ = ('list',)

    def getValues(self, request):
      obj = request
      for key in self.stateKey.split("."): obj = getattr(obj, key)
      return map(self.getValue, obj)
    def getKeys(self, request):
      obj = request
      for key in self.stateKey.split("."): obj = getattr(obj, key)
      return map(self.getKey, obj)
    def getItems(self, request):
      obj = request
      for key in self.stateKey.split("."): obj = getattr(obj, key)
      return obj
    def hasCustom(self, request):
      return len(filter(None, map(lambda item: getattr(item, self.custom_attribute, False),self.getItems(request)))) > 0

    def keyToPython(self, value, state = None):
        return value

    def customValueToPython(self, value, state = None):
        return value

    def _to_python(self, value, state):
        if isinstance(value, dict):
          custom = self.customValueToPython(value.get("custom", None), state)
          val = self.keyToPython(value.get("value", None), state)
          items = {self.getKey(s):getattr(s, self.custom_attribute, False) for s in self.getItems(state)}
          is_custom = items.get(val, False)
        else:
          is_custom = False
          val = self.keyToPython(value, state)
        self.list = self.getKeys(state)
        if not val in self.list:
            if self.hideList:
                raise Invalid(self.message('invalid', state), val, state)
            else:
                try:
                    items = '; '.join(map(str, self.list))
                except UnicodeError:
                    items = '; '.join(map(unicode, self.list))
                raise Invalid(
                    self.message('notIn', state,
                        items=items, val=val), val, state)
        else:
            # breaking change: this was
            # return custom if is_custom and custom else val

          return custom if is_custom else val

    validate_python = formencode.FancyValidator._validate_noop
class OneOfStateNoCustom(OneOfState):
    def hasCustom(self, req):
        return False

class OneOfStateInt(OneOfState):
    def keyToPython(self, value, state):
        if value is None: return None
        try:
            return int(value)
        except:
            raise Invalid(self.message('invalid', state), value, state)


class DateValidator(formencode.FancyValidator):
  messages = dict(
        badFormat=_('Please enter the date in the form %(format)s'),
        monthRange=_('Please enter a month from 1 to 12'),
        invalidDay=_('Please enter a valid day'),
        dayRange=_('That month only has %(days)i days'),
        invalidDate=_('That is not a valid day (%(exception)s)'),
        unknownMonthName=_('Unknown month name: %(month)s'),
        invalidYear=_('Please enter a number for the year'),
        fourDigitYear=_('Please enter a four-digit year after 1899'),
        wrongFormat=_('Please enter the date in the form %(format)s')
    )
  def _to_python(self, value, state):
    try:
      value = datetime.strptime(value, self.format)
      if value.year < 1900:
        raise formencode.Invalid(self.message('fourDigitYear', state), value, state)
    except ValueError, e:
      raise formencode.Invalid(self.message("badFormat", state, format = self.format.replace('%d', 'dd').replace('%m', 'mm').replace('%Y', 'yyyy')), value, state)
    else: return value
      
class DecimalValidator(formencode.FancyValidator):
  is_number_validator = True
  step = 0.01
  messages = {"invalid_amount":_(u'Bitte eine Zahl eingeben'),
        "amount_too_high":_(u"Bitte eine Zahl %(max_amount)s oder kleiner eingeben"),
        "amount_too_low":_(u"Bitte eine Zahl %(min_amount)s oder größer eingeben")
      }
  max = None
  min = None
  def _to_python(self, value, state):
    if not getattr(self, 'required', False) and not value:
        return getattr(self, 'if_missing', None)
    try:
      value = parse_decimal(value, locale = state._LOCALE_)
      if self.max and value > self.max:
        raise formencode.Invalid(self.message("amount_too_high", state, max_amount = format_decimal(self.max, locale=state._LOCALE_)), value, state)
      if self.min and value < self.min:
        raise formencode.Invalid(self.message("amount_too_low", state, min_amount = format_decimal(self.min, locale=state._LOCALE_)), value, state)
    except NumberFormatError, e:
      raise formencode.Invalid(self.message("invalid_amount", state, value = value), value, state)
    except ValueError, e:
      raise formencode.Invalid(self.message("amount_too_high", state, max_amount = format_decimal(self.max, locale=state._LOCALE_)), value, state)
    else: return value


def TypeAheadValidator(attrs):
    if attrs.required:
        validator = formencode.validators.String(required = True)
    else:
        validator = formencode.validators.String(required = False, not_empty = False, if_missing= None)
    return formencode.Schema(name = validator, token = validator, filter_extra_fields = True)
