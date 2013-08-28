import ConfigParser, sys, getopt, os
from datetime import datetime
import logging, time
from larryslist import Globals
from larryslist.website.apps.contexts import config_loader
from larryslist.website.apps import WebsiteSettings

log = logging.getLogger()
log.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
log.addHandler(ch)


APP_SECTION = 'app:larryslist'



class FakeContext(object):
    def __init__(self, settings):self.settings = settings
class FakeRequest(object):
    def __init__(self, globals, settings):
        self.globals = globals
        self.backend = globals.backend
        self.root = FakeContext(settings)
def get_fake_request(config):
    g = Globals(**config)
    g.setSettings(WebsiteSettings, config)
    settings = getattr(g, WebsiteSettings.key)
    return FakeRequest(g, settings)


class Usage(Exception):
    def __init__(self, msg):self.msg = msg

def get_config(configname):
    _config = ConfigParser.ConfigParser({'here':os.getcwd()})
    _config.optionxform = str
    _config.read(configname)
    _config = dict(_config.items(APP_SECTION))
    return _config



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
    request = get_fake_request(config)
    ta = request.globals.typeahead_search

    while True:
        start = datetime.now()
        webconfig = config_loader.get(request)
        ta.index('MEDIA', webconfig.usedMedia)
        ta.index('GENRE', webconfig.Genre)
        ta.index('COUNTRY', webconfig.Country)
        ta.index('ORIGIN', webconfig.Origin)
        ta.index('CITY', webconfig.City)
        ta.index('ARTIST', webconfig.Artist)
        log.info('CHECKING TYPEAHEAD SEARCHES in %s', datetime.now() - start)
        time.sleep(10)



if __name__ == "__main__":
    sys.exit(main())