import ConfigParser, sys, getopt, os
from datetime import datetime
import time
from larryslist import Globals
from larryslist.tasks.typeahead import TypeAheadSearch, get_typeahead_conn

from larryslist.website.apps.contexts import GetWebConfigProc
from larryslist.website.apps import WebsiteSettings

APP_SECTION = 'app:larryslist'

class FakeContext(object):
    def __init__(self, settings):
        self.settings = settings
class FakeRequest(object):
    def __init__(self, globals, settings):
        self.backend = globals.backend
        self.root = FakeContext(settings)

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg

def get_config(configname):
    _config = ConfigParser.ConfigParser({'here':os.getcwd()})
    _config.optionxform = str
    _config.read(configname)
    _config = dict(_config.items(APP_SECTION))
    return _config

def get_fake_request(config):
    g = Globals(**config)
    g.setSettings(WebsiteSettings, config)
    settings = getattr(g, WebsiteSettings.key)
    return FakeRequest(g, settings)


def main(argv=None):
    if argv is None:
        argv = sys.argv
    try:
        opts, args = getopt.getopt(sys.argv[1:], "f:h", ["help", "file"])
        opts = dict(opts)
        if '-f' not in opts:
            raise Usage("Missing Option -f")
    except getopt.error, msg:
         raise Usage(msg)
    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

    configname = opts['-f']
    config = get_config(configname)
    webconfig = GetWebConfigProc(get_fake_request(config))

    conn = get_typeahead_conn(config)
    ta = TypeAheadSearch('larryslist', conn, 600)
    while True:
        start = datetime.now()
        ta.index('ARTIST', webconfig.Artist)
        ta.index('CITY', webconfig.City)
        ta.index('MEDIA', webconfig.Medium)
        ta.index('GENRE', webconfig.Genre)
        ta.index('COUNTRY', webconfig.Country)
        ta.index('ORIGIN', webconfig.Origin)
        print 'CHECKING TYPEAHEAD SEARCHES in', datetime.now() - start
        time.sleep(10)



if __name__ == "__main__":
    sys.exit(main())