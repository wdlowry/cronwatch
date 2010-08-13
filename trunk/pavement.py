from paver.easy import *
from paver.setuputils import setup, install_distutils_tasks
    
setup(
    name = 'cronwatch',
    version = '1.0',
    description = 'A script that monitors cron job output',
    author = 'David Lowry',
    author_email = 'wdlowry@gmail.com',
    url = 'http://code.google.com/p/cronwatch/',
    license = 'GPL2',
    scripts = ['cronwatch'],
    test_suite = 'nose.collector',
    install_requires=['configobj']
)

options(
    sphinx=Bunch(
        docroot = 'docs',
        builddir = 'build',
        sourcedir = 'source'
    )
)

@task
@needs('paver.doctools.html')
def html():
    pass

@task
@needs('generate_setup', 'minilib', 'html', 'setuptools.command.sdist')
def sdist():
    '''Overrides sdist to make sure that our setup.py is generated.'''

