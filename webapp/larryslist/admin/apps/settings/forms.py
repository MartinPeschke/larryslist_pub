from jsonclient.backend import DBMessage
from larryslist.admin.apps.settings.models import CreateUserProc
from larryslist.lib.baseviews import GenericSuccessMessage
from larryslist.lib.formlib.formfields import BaseForm, StringField, EmailField, MultipleFormField, TokenTypeAheadField, TagSearchField, ConfigChoiceField, REQUIRED


class CountrySearchField(TagSearchField):
    template = "larryslist:admin/templates/settings/country.html"

class FeederCreateForm(BaseForm):
    fields = [
        #ConfigChoiceField("type", "Role", "FeederRole", attrs = REQUIRED)
        StringField("name", "Name")
        , EmailField("email", "Email")
        , StringField("pwd", "Password")
        , CountrySearchField('Country', "Country", "/admin/search/address", "AddressSearchResult", api_allow_new = False, query_extra={'type':'Country'}, classes='tagsearch input-xxlarge')
    ]

    @classmethod
    def on_success(cls, request, values):
        try:
            result = CreateUserProc(request, values)
        except DBMessage, e:
            result = {'success':False, 'errors':{}, 'values':values}
            if e.message == 'EMAIL_TAKEN':
                result['errors'] = {'email':"Email already taken"}
            else:
                result['message'] = e.message
            return result
        request.session.flash(GenericSuccessMessage("New user {name} ({email}) created".format(**values)), "generic_messages")
        return {'success':True, 'redirect':request.fwd_url("admin_settings_feeder_create")}