from paver.easy import *
from paver.setuputils import setup

#copy_file('cronwatch.py', 'cronwatch')
setup(name = 'cronwatch',
      version = '1.0',
      url = 'http://code.google.com/p/cronwatch/',
      author = 'David Lowry',
      author_email = 'wdlowry@gmail.com',
      scripts = ['cronwatch'])


@task
@needs('generate_setup', 'minilib', 'setuptools.command.sdist')
def sdist():
    '''Overrides sdist to make sure that our setup.py is generated.'''

