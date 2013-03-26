from datetime import datetime, date
from larryslist.lib import i18n
from larryslist.lib.request import extend_request
from larryslist.lib.subscribers import context_authorization, add_renderer_variables
from pyramid.config import Configurator
from larryslist.lib.i18n import DefaultLocaleNegotiator, add_localizer
from larryslist.lib.globals import Globals
from pyramid.mako_templating import renderer_factory
from pyramid.renderers import JSON
from pyramid_beaker import session_factory_from_settings, set_cache_regions_from_settings


jsonRenderer = JSON()
jsonRenderer.add_adapter(datetime, i18n.format_date)
jsonRenderer.add_adapter(date, i18n.format_date)

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """

    settings["g"] = g = Globals(**settings)
    config = Configurator(settings=settings
        , session_factory = session_factory_from_settings(settings)
        , locale_negotiator = DefaultLocaleNegotiator(g.available_locales, g.default_locale_name))


    extend_request(config)

    config.add_translation_dirs('formencode:i18n')
    config.add_translation_dirs('larryslist:locale')

    config.add_renderer(".html", renderer_factory)
    config.add_renderer(".xml", renderer_factory)
    config.add_renderer('json', jsonRenderer)

    config.add_subscriber(add_localizer, 'pyramid.events.NewRequest')
    config.add_subscriber(context_authorization, 'pyramid.events.ContextFound')
    config.add_subscriber(add_renderer_variables, 'pyramid.events.BeforeRender')

    if g.is_debug:
        config.add_static_view('static', 'static', cache_max_age=3600)

    if settings['deploy.admin'] == 'True':
        config.include("larryslist.admin.apps", route_prefix='/admin')
    if settings['deploy.website']:
        config.include("larryslist.website.apps")
    if settings['deploy.reports'] =='True':
        config.include("larryslist.reports.apps", route_prefix='/reports')

    config.scan()
    return config.make_wsgi_app()