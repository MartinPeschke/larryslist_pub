import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid>=1.4a3',
    'pyramid_debugtoolbar',
    'formencode',
    'pastescript',
    'pastedeploy',
    'mako',
    'babel',
    'lingua',
    'beaker',
    'paste',
    'simplejson',
    'dnspython',
    'turbomail',
    'uuid',
    'pyramid_beaker',
    'pyramid_exclog',
    'beautifulsoup',
    'unidecode',
    'jsonclientHGMMP>=0.0.504',
    "dogpile.cache>=0.4.1"
    ]

setup(name='larryslist',
      version='0.1',
      description='larryslist',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Programming Language :: Pyramid",
        "Framework :: Pylons",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pyramid',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      install_requires=requires,
      tests_require=requires,
      test_suite="larryslist",
      message_extractors = {
            'larryslist': [
                ('**.py', 'lingua_python', None),
                ('website/templates/**.html', 'mako', {'input_encoding': 'utf-8'}),
                ('website/templates/**.js', 'mako', {'input_encoding': 'utf-8'})
                ]
             },
      entry_points = """\
      [paste.app_factory]
      main = larryslist:main
      """,
      )

