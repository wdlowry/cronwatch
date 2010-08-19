from paver.easy import *
from paver.setuputils import setup, install_distutils_tasks

VERSION = '1.0'

setup(
    name = 'cronwatch',
    version = VERSION,
    description = 'A script that monitors cron job output',
    long_description = 'cronwatch is a Python script that executes programs ' +
                       'and captures their output and exit codes and ' +
                       ' handles that output as configured.',
    author = 'David Lowry',
    author_email = 'wdlowry@gmail.com',
    url = 'http://code.google.com/p/cronwatch/',
    download_url = 'http://cronwatch.googlecode.com/files/%s.tar.gz' % VERSION,
    license = 'GPL',
    classifiers = [ 'Development Status :: 5 - Production/Stable',
                    'Environment :: Console',
                    'Intended Audience :: System Administrators',
                    'License :: OSI Approved :: GNU General Public License ' +
                        '(GPL)',
                    'Operating System :: POSIX',
                    'Topic :: System :: Logging',
                    'Topic :: System :: Systems Administration',
                  ],
    platforms = ['Any'],
    scripts = ['cronwatch'],
    test_suite = 'nose.collector',
    requires=['configobj'],
    zip_safe=False,
)

options(
    sphinx=Bunch(
        docroot = 'docsrc',
        builddir = 'build',
        sourcedir = 'source'
    )
)

@task
@needs('paver.doctools.html')
def html():
    '''Build cronwatch's docs and put them in docs/'''
    builtdocs = path(options.sphinx.docroot) / options.sphinx.builddir / 'html'
    destdir = path('docs')
    destdir.rmtree()
    builtdocs.move(destdir)

@task
@needs('generate_setup', 'minilib', 'html', 'setuptools.command.sdist')
def sdist():
    '''Overrides sdist to make sure that our setup.py is generated.'''

