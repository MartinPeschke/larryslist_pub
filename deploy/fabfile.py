"""
  easy_install mako
"""
from fabric.api import local
from fabric.api import run, local, run, cd, lcd, put
from fabric.contrib import files

import shutil, os, md5, fabric
from datetime import datetime
from collections import namedtuple
from mako.template import Template
SubSite = namedtuple("SubSite", ["location", "scripts", "styles"])
Style = namedtuple("Style", ["list", "hasBuster"])

############## CONFIG #########################

PROJECTNAME="larryslist"
SUBSITES = [
    SubSite(location = 'website', scripts=['jquery.placeholder.js', 'store.js', 'setup.js'], styles=Style(['site.less'], True))
    , SubSite(location = 'admin', scripts=["setup.js"], styles=Style(['site.less'], True))
  ]
PROCESS_GROUPS = ['p1', 'p2']
CLEAN_SESSIONS = False


UPDATE_CMDS = {
    'dev':"git clone git@github.com:HarryMcCarney/LarrysList.git"
}



EXTRA_SETUP = [
    './env/bin/easy_install redis'
    , './env/bin/easy_install hiredis'
    , './env/bin/pip install git+git://github.com/bbangert/beaker_extensions.git'
]

############## DONT TOUCH THIS ################

root = '/server/www/{}/'.format(PROJECTNAME)
def get_deploy_path(env):
  return "{}{}/".format(root, env)
def get_code_path(env, version):
    return '{}code/{}/'.format(get_deploy_path(env), version)
def getShortToken(version):
    return md5.new(version).hexdigest()

def clean_remote(env):
  environment_path = get_deploy_path(env)
  with cd(environment_path):
    run("rm -rf env/*")
    run("rm -rf repo.git/*")
    run("rm -rf repo.git/.git*")
    run("virtualenv --no-site-packages env")
    run("env/bin/easy_install supervisor")

def create_env(env):
  with cd(root):
    run("mkdir -p {}/{{run,logs,code,env,repo.git}}".format(env))

  clean_remote(env)
  cfg_template = Template(filename='supervisor.cfg.mako')
  with cd(get_deploy_path(env)):
    files.append("supervisor.cfg", cfg_template.render(env = env), escape=False)
    run("env/bin/supervisord -c supervisor.cfg")
    with cd("repo.git"):
        run(UPDATE_CMDS[env])
    for extra in EXTRA_SETUP:
        run(extra)

def update(env):
  with cd("{}repo.git".format(get_deploy_path(env))):
    run("git pull")

def build(env, version):
  environment_path = get_deploy_path(env)
  code_path = get_code_path(env, version)

  run("mkdir {}".format(code_path))
  with cd(code_path):
    run("cp -R {}repo.git/webapp/* .".format(environment_path))

def build_statics(env, version):
    code_path = get_code_path(env, version)
  
    # build player skin
    with cd(code_path):
        for subsite in SUBSITES:
            loc = subsite.location
            def getPath(path):
                return "{project}/{subsite}/static/{path}".format(project=PROJECTNAME, subsite=loc, path=path)

            style = subsite.styles
            if not files.exists(getPath("css")):
                run("mkdir -p {}".format(getPath("css")))

            if style.hasBuster:
                files.sed(getPath("less/cachebuster.less"), "CACHEBUSTTOKEN", '"{}"'.format(getShortToken(version)))

            for stylesheet in style.list:
                run("~/node_modules/less/bin/lessc {project}/{subsite}/static/less/{stylesheet} --yui-compress {project}/{subsite}/static/css/{outname}.min.css".format(project=PROJECTNAME, subsite=loc, stylesheet=stylesheet, outname = stylesheet.rsplit(".")[0]))


        if not files.exists("{project}/static/scripts/build/".format(project=PROJECTNAME)):
            run("mkdir -p {project}/static/scripts/build/".format(project=PROJECTNAME))
        run("java -jar ~/resources/compiler.jar --compilation_level SIMPLE_OPTIMIZATIONS \
            --js \
            {project}/static/scripts/libs/bootstrap.js \
            {project}/static/scripts/libs/JSON.js \
            {project}/static/scripts/libs/store.js \
            {project}/static/scripts/libs/underscore.js \
            {project}/static/scripts/libs/backbone.js  \
            {project}/static/scripts/libs/jquery.validate.js \
            {project}/static/scripts/libs/require.js \
            --warning_level QUIET --js_output_file {project}/static/scripts/build/libs.js".format(project=PROJECTNAME))

        for subsite in SUBSITES:
            if not files.exists("{project}/{subsite}/static/scripts/build/".format(project=PROJECTNAME, subsite=subsite.location)):
                run("mkdir -p {project}/{subsite}/static/scripts/build/".format(project=PROJECTNAME, subsite=subsite.location))

            customs = " ".join(["{project}/{subsite}/static/scripts/{script}".format(project=PROJECTNAME, subsite=subsite.location, script = script) for script in subsite.scripts])
            run("java -jar ~/resources/compiler.jar --compilation_level SIMPLE_OPTIMIZATIONS \
                --js {customs} \
                --warning_level QUIET --js_output_file {project}/{subsite}/static/scripts/build/site.js".format(project=PROJECTNAME, subsite=subsite.location, customs = customs))
        run("echo {} > ./VERSION_TOKEN".format(getShortToken(version)))



def switch(env, version):
    environment_path = get_deploy_path(env)
    code_path = get_code_path(env, version)

    if CLEAN_SESSIONS:
        result = run("redis-cli flushall")

    with cd(environment_path):
        run("cp {}{}.ini {}code".format(code_path, env, environment_path))
        run("env/bin/python {}setup.py develop".format(code_path))
        with cd("code"):
            run("rm current;ln -s {} current".format(version))
        for pg in PROCESS_GROUPS:
            result = run("env/bin/supervisorctl -c supervisor.cfg restart {}:*".format(pg), pty=True)
            if "ERROR" in result:
              run("tail -n50 logs/python*.log", pty=True)
              fabric.utils.abort("Process group did not start:{}: {}".format(pg, result))


def deploy(env):
  VERSION_TOKEN = datetime.now().strftime("%Y%m%d-%H%M%S-%f")[:-3]
  update(env)
  build(env, VERSION_TOKEN)
  build_statics(env, VERSION_TOKEN)
  switch(env, VERSION_TOKEN)