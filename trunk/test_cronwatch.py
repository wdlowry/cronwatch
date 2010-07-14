#!/usr/bin/python
# $Id$
# vim:ft=python:sw=4:sta:et
#
# test_cronwatch.py - Unit tests for cronwatch
# Copyright (C) 2010 David Lowry  < wdlowry at gmail dot com >
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.

import unittest
from tempfile import NamedTemporaryFile
from StringIO import StringIO
from test_base import TestBase

import cronwatch

###############################################################################
# Cronwatch functionality tests
###############################################################################
class TestCommandLine(TestBase):
    '''Test the command line functionality
       
       Note: The command line options will not be tested. See the comment for
             main().'''

    def test_empty_command_line(self):
        '''Should raise an error if the executable is missing from the command
           line'''

        self.assertRaisesError(cronwatch.Error,
                               'missing command line argument: executable',
                               cronwatch.main, ['cronwatch'])

class TestRun(TestBase):
    '''Test the run() function'''

    def test_run_error(self):
        '''Should throw an exception when there's an error running the 
           executable'''
        self.assertRaisesError(cronwatch.Error,
            'could not run missing: [Errno 2] No such file or directory',
            cronwatch.run, ['missing'])

    def test_simple_output(self):
        '''Should return the output'''

        (o, r) = cronwatch.run(['./test_script.sh', 'simple'])
        
        self.assertEquals(10, r)
        o = o.read()
        self.assertEquals('stdout\nstderr\nstdout again\n', o)

    def test_stdin(self):
        '''Should close stdin just to be safe'''

        # This will hang if something is not done about stdin
        (o, r) = cronwatch.run(['./test_script.sh', 'read'])
        
        self.assertEquals(0, r)
        o = o.read()
        self.assertEquals('\n', o)

    def test_timeout(self):
        '''Should timeout and terminate the process'''

        (o, r) = cronwatch.run(['./test_script.sh', 'timeout'], 0)
        
        self.assertEquals(-1, r)
        o = o.read()
        self.assertEquals('', o)

class TestFilterText(TestBase):
    '''Test the filter_text function'''
    
    # results = filter_text (regex, fh)
    # results = { 'regex1': [result lines], 'regex2', [result lines] }
    # regex can be a single regex or list

    def setUp(self):
        self.tmp = StringIO()

    def tearDown(self):
        self.tmp.close()

    def write(self, contents):
        '''Write contents to the temporary file'''
        self.tmp.write(contents)
        self.tmp.flush()
        self.tmp.seek(0)

    def test_simple(self):
        '''Should find the lines with the search expression'''
        self.write('one\ntwo\nthree\n')
        r = cronwatch.filter_text('e', self.tmp)
        self.assertEqual({'e': [0, 2]}, r)

    def test_complex(self):
        '''Should accept a list of regexes'''
        self.write('one\ntwo\nthree\n')
        r = cronwatch.filter_text(['one', 'o', 'none'], self.tmp)
        self.assertEqual({'one': [0], 'o': [0, 1], 'none': []}, r) 

    def test_bad_regex(self):
        '''Should throw an error if the the regex is bad'''
        self.assertRaisesError(cronwatch.Error,
                'invalid regex "(": unbalanced parenthesis',
                cronwatch.filter_text, '(', self.tmp)

class TestReadConfig(TestBase):
    '''Test the read_config() function'''

    def setUp(self):
        self.old_config = cronwatch.CONFIGFILE
        cronwatch.CONFIGFILE = 'this_is_not_a_file.forsure'

    def tearDown(self):
        cronwatch.CONFIGFILE = self.old_config
    
    def test_defaults(self):
        '''Should set defaults if no config is found'''
        c = cronwatch.read_config()
        
        c.test.a = 1
        self.assertEquals(None, c.test.required)
        self.assertEquals('.*', c.test.blacklist)
        self.assertEquals(None, c.test.whitelist)
        self.assertEquals(0, c.test.exit_codes)
        self.assertEquals('root', c.test.email)
        self.assertEquals(4096, c.test.email_maxsize)
        self.assertEquals(False, c.test.email_success)
        self.assertEquals('/usr/lib/sendmail', c.test.email_sendmail)
        self.assertEquals(None, c.test.logfile)

    def test_default_configfile(self):
        '''Should read the main configuration file if it exists'''
        cf = NamedTemporaryFile()
        cf.write('[job]\n')
        cf.write('exit_codes=10\n')
        cf.write('exit_codes=101\n')
        cf.seek(0)

        cronwatch.CONFIGFILE = cf.name

        c = cronwatch.read_config()

        self.assertEquals([10, 101], c.job.exit_codes)

    def test_configfile_command_line(self):
        '''Should read an alternate config file'''
        cf = NamedTemporaryFile()
        cf.write('[fake]\n')
        cf.write('required = stuff\n')
        cf.seek(0)

        cronwatch.CONFIGFILE = cf.name

        cf2 = NamedTemporaryFile()
        cf2.write('[job]\n')
        cf2.write('exit_codes = 1\n')
        cf2.seek(0)

        c = cronwatch.read_config(config_file = cf2.name)

        self.assertFalse(c.has_section('fake'))
        self.assertEquals(1, c.job.exit_codes)

    def test_require_configfile(self):
        '''Should raise an exception if the config file doesn't exist'''
        self.assertRaises(IOError, cronwatch.read_config, 
                          'this_is_not_a_file.forsure')

    def test_unknown_option(self):
        '''Should raise an exception if it encounters an unknown configuration
           option'''
        cf = NamedTemporaryFile()
        cf.write('bad_option = stuff\n')
        cf.seek(0)

        self.assertRaisesError(cronwatch.Error,
                'unknown option bad_option in section main',
                cronwatch.read_config, cf.name)

class TestWatch(TestBase):
    '''Test the watch() function'''

if __name__ == '__main__':
    unittest.main()
