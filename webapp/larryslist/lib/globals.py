from jsonclient.backend import VersionedBackend
import logging, os, random
from larryslist.tasks.typeahead import get_typeahead_conn, TypeAheadSearch

log = logging.getLogger(__name__)


APP_ROOT = os.path.abspath(os.path.join(__file__, "..", "..", ".."))
VERSION_FILE = os.path.join(APP_ROOT, "VERSION_TOKEN")

if os.path.exists(VERSION_FILE):
    VERSION_TOKEN = open(VERSION_FILE).read().strip()
else:
    VERSION_TOKEN = random.random()
log.info("USING NEW STATIC RESOURCE TOKEN: %s", VERSION_TOKEN)

from dogpile.cache import make_region



class Globals(object):
    mailConfig = {"mail.on":True,"mail.transport":"smtp", "mail.smtp.tls":True}
    def __init__ (self, **settings):
        self.is_debug = settings.get('pyramid.debug_templates', 'false') == 'true'
        self.VERSION_TOKEN = "v={}".format(VERSION_TOKEN)

        backend_options = dict(location = settings['deploy.api.url'], version = settings['deploy.api.version'])
        backend_options['http_options'] = dict( disable_ssl_certificate_validation = True )
        self.backend = VersionedBackend(**backend_options)
        self.project_name = settings['project.name']
        self.site_slogan = settings['project.site_slogan']
        self.secure_scheme = settings['deploy.secure_scheme']
        self.uploadUrl = settings['deploy.upload_url']
        self.resourceHost = settings['deploy.resource_host']

        self.available_locales = settings['pyramid.available_locales'].split()
        self.default_locale_name = settings['pyramid.default_locale_name']

        self.mailConfig.update({"mail.smtp.server":settings['email.host']
            ,"mail.smtp.username":settings['email.user']
            ,"mail.smtp.password":settings['email.pwd']
            ,"mail.smtp.port":settings['email.port']
        })
        self.mailRecipient = settings['email.recipient']

        self.setupDBConfig(self.backend)

        self.cache = make_region().configure_from_config(settings, "cache.")
        self.typeahead_search = TypeAheadSearch('larryslist', get_typeahead_conn(settings))

    def getMailConfig(self):
        return self.mailConfig

    def setSettings(self, cls, settings):
        s = cls({s.replace("{}.".format(cls.key), ""):settings[s] for s in settings.keys() if s.startswith("{}.".format(cls.key))})
        setattr(self, cls.key, s)

    def setupDBConfig(self, backend):
        pass



