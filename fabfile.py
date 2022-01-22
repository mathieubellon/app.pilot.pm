import os
import sys

from fabric.api import task, local, settings, abort, execute
from fabric.colors import green, red, blue, yellow, white, cyan
import requests


@task
def watch(lan=False):
    """
    Run webpack during development
    Watches for changes in JS and SCSS
    Look at webpack.config.js for build config
    """
    if lan:
        nodeServerHost = local("ipconfig getpacket en0 | grep yiaddr| awk '{print $3}'", capture=True)
        os.environ['LAN_IP'] = nodeServerHost

    local('yarn --cwd ./front run serve')

@task
def build():
    """
    Essentially package statics with webpack
    :return:
    """
    print(blue('\nPackage statics with webpack for production environment (take some time) \n'))
    local('yarn --cwd ./front run build')


@task
def migrate():
    """
    Apply DB migration
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.dev')
    local('python back/manage.py migrate')


@task
def worker():
    """
    Apply DB migration
    """
    local('python back/run_rq_worker.py')

@task
def devserver(runserverCommand='runserver', host='127.0.0.1', port=8000,
              nodeServerHost='localhost', nodeServerPort=3000, settings="dev", lan=False):
    """
    Runs development server

    If you do       => $ fab watch:nodeServerPort=8033
    You have to do  => $ fab devserver:nodeServerPort=8033
    Because the devserver listen to the node server that delivers all webpack builded statics files live from memory

    """
    if lan:
        host = local("ipconfig getpacket en0 | grep yiaddr| awk '{print $3}'", capture=True)
        nodeServerHost = local("ipconfig getpacket en0 | grep yiaddr| awk '{print $3}'", capture=True)

    print(cyan('%s' % host))
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.dev')
    print(green('Dev settings loaded'))
    try:
        r = requests.get('http://{nodeServerHost}:{nodeServerPort}'.format(nodeServerHost=nodeServerHost, nodeServerPort=nodeServerPort))
        print(green('Listening to Webpack dev server on http://{nodeServerHost}:{nodeServerPort}'.format(nodeServerHost=nodeServerHost, nodeServerPort=nodeServerPort)))
        print(green('Reading from webpack-stats-dev.json'))
    except:
        print(yellow('Webpack dev server is *not* running, reading webpack-stats.json'))
        settings = 'dev_no_webpack_server'
    print(green('\nRun development server on http://{host}:{port}\n'.format(host=host, port=port)))
    local('python back/manage.py {runserverCommand} {host}:{port} --settings=settings.{settings}'.format(
        runserverCommand=runserverCommand, host=host, port=port, settings=settings
    ))

@task
def clean():
    """ Delete all pyc,mo, .. files """
    local('find . "(" -name "*.pyc" -or -name "*.pyo" \
            -or -name "__pycache__" ")" -delete')
    local('find . -type d -empty -delete')


def maybe_build_statics(buildstatics):
    if buildstatics is not None:
        print(blue('Tests must run against ready for production packaged static to avoid bizareness \n'))
        build()

        print(blue('Collect & Compress statics'))
        local('python back/manage.py collectstatic --noinput')

@task
def tests_python(testname='pilot', buildstatics=None):
    """Runs Pilot pyhon tests locally.
    testname : used to choose test to launch (default : all tests)
    buildstatics: rebuild the static files if specified to any value
    Call example : fab tests_python:pilot/items,buildstatics=1
    will rebuild the statics, then launch 'py.test pilot/items'
    """

    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.tests')
    print(blue('Reading webpack-stats.json'))

    maybe_build_statics(buildstatics)

    print(blue('Running python tests with py.test'))
    local('py.test --reuse-db --tb=short %s --ds=settings.tests' % testname)

    # if testrun.failed and not confirm("Tests failed. Continue anyway?"):
    #     abort("Aborting at user request.")

@task
def tests_jest_unit(testname='', buildstatics=None):
    """Runs Pilot jest unit tests locally.
    testname : used to choose tests to launch (default : all tests)
    buildstatics: rebuild the static files if specified to any value
    Call example : fab tests_jest_unit:pilot_users,buildstatics=1
    will rebuild the statics, then launch 'npm run-script unittest pilot_users'
    """

    maybe_build_statics(buildstatics)

    print(blue('Running js unit tests with jest'))
    local('npm run-script unittest %s' % testname)

@task
def tests_functional(testname='', env='', noserver=False, buildstatics=None):
    """Runs Pilot jest functional tests locally.
    testname : used to choose tests to launch (default : all tests)
    buildstatics: rebuild the static files if specified to any value

    Call example : fab tests_functional:pilot_users,env=debug,buildstatics=1

    will rebuild the statics, then launch 'npm run-script functionaltest -f *pilot_users*.js -e debug'

    When using the "noserver" option, you should start the test server manually :
    python manage.py nightwatch_test_server --addrport 0.0.0.0:8001 --settings=settings.tests --keepdb --noinput
    """

    maybe_build_statics(buildstatics)

    print(blue('Running js functional tests with jest'))

    args = []

    if testname:
        args.append('-f *%s*.js' % testname)
    if env:
        args.append('-e %s' % env)
    if noserver:
        args.append('--noserver')

    command = 'npm run-script functionaltest'
    if args:
        command += ' -- ' + ' '.join(args)

    local(command)


@task
def tests(buildstatics=None):
    """Runs all pilot tests locally.
    buildstatics: rebuild the static files if specified to any value
    Call example : fab tests:buildstatics=1
    """
    maybe_build_statics(buildstatics)

    tests_python()
    # tests_jest_unit()
    # 14/03/18 : There's currently an issue with chromedriver 0.36 + chrome 65
    # where nightwatch browser.setValue does not works.
    # We need to freeze versions that do work.
    # tests_functional()


@task
def doc():
    """
    Generate integration API documentation in OpenAPI format
    """
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.dev')
    local('python back/manage.py generate_integrations_doc')


