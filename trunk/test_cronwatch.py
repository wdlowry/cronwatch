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
import os
from tempfile import NamedTemporaryFile, TemporaryFile, mkdtemp
from StringIO import StringIO
from shutil import rmtree
from test_base import TestBase
from getpass import getuser
from socket import getfqdn, gethostname
from validate import VdtTypeError, VdtValueError
from configobj import get_extra_values


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

class TestIsRegex(TestBase):
    def test_not_string(self):
        '''Should raise VdtTypeError if it's not a string'''
        self.assertRaises(VdtTypeError, cronwatch.is_regex, 1)

    def test_bad_regex(self):
        '''Should raise VdtValueError if it's not a valid regex'''
        self.assertRaisesError(cronwatch.VdtValueMsgError,
                '''invalid regular expression: (: unbalanced parenthesis''',
               cronwatch.is_regex, '(')

    def test_return(self):
        '''Should return a valid regular expression object'''
        self.assertTrue(cronwatch.is_regex('reg').match)

class TestIsRegexList(TestBase):
    def test_not_list(self):
        '''Should raise VdtTypeError if not a list'''
        self.assertRaises(VdtTypeError, cronwatch.is_regex_list, 'reg')

    def test_regex(self):
        '''Should return a list of regex objects'''
        self.assertTrue(cronwatch.is_regex_list(['reg', 'reg'])[0].match)

class TestForceRegexList(TestBase):
    def test_list(self):
        '''Should return a list of regex objects if already in list form'''
        self.assertTrue(cronwatch.force_regex_list(['reg', 'reg'])[0].match)

    def test_not_list(self):
        '''Should create a list if not a list already'''
        self.assertTrue(cronwatch.force_regex_list('reg')[0].match)

class TestForceIntList(TestBase):
    def test_list(self):
        '''Should return a list of integers if already in list form'''
        self.assertEquals([1, 2], cronwatch.force_int_list(['1', '2']))

    def test_not_list(self):
        '''Should create a list if not a list already'''
        self.assertEquals([1], cronwatch.force_int_list(1))

#    
#    def test_exit_codes(self):
#        '''Should verify and normalize the exit_codes'''
#        c = self.config()
#        c.main.exit_codes = 1
#        cronwatch.verify_config(c)
#        self.assertEquals([1], c.main.exit_codes)
#
#        c.main.exit_codes = [1, 2]
#        cronwatch.verify_config(c)
#        self.assertEquals([1, 2], c.main.exit_codes)
#
#        c.main.exit_codes = [1, 'a']
#        self.assertRaisesError(cronwatch.Error, 
#                'configuration error: ' +
#                'main.exit_codes must be a list of integer exit codes',
#                cronwatch.verify_config, c)
#
#    def test_email_maxsize(self):
#        '''Should verify it is a integer'''
#        c = self.config()
#        c.main.email_maxsize = 10
#        cronwatch.verify_config(c)
#        self.assertEquals(10, c.main.email_maxsize)
#
#        c.main.email_maxsize = 'a'
#        self.assertRaisesError(cronwatch.Error,
#                'configuration error: main.email_maxsize must be an integer',
#                cronwatch.verify_config, c)
#
#    #def test_strings(self):
#    #    '''Should verify that certain options are strings'''
#    #    for s in ['email_to', 'email_from', 'email_sendmail', 'logfile']:
#    #        c = self.config()
#    #        c.set_setting('main', s, 1)
#    #        self.assertRaisesError(cronwatch.Error,
#    #                'configuration error: main.%s must be a string' % s,
#    #                cronwatch.verify_config, c)
#    #        c.set_setting('main', s, 'value')
#    #        cronwatch.verify_config(c)
#    #        self.assertEqual('value', c.get_setting(main, 's'))
#

class TestReadConfig(TestBase):
    '''Test the read_config() function'''

    def setUp(self):
        self.old_config = cronwatch.CONFIGFILE
        cronwatch.CONFIGFILE = 'this_is_not_a_file.forsure'

    def tearDown(self):
        cronwatch.CONFIGFILE = self.old_config

    def test_parse_error(self):
        '''Should raise an error when the config file is bad'''
        cf = NamedTemporaryFile()
        cf.write('[test\n')
        cf.seek(0)
        self.assertRaisesError(cronwatch.Error,
                'could not read %s: Invalid line at line "1".' % cf.name, 
                cronwatch.read_config, cf.name)

    def test_defaults(self):
        '''Should set defaults if no config is found'''
        cf = NamedTemporaryFile()
        cf.write('[test]\n')
        cf.seek(0)
        c = cronwatch.read_config(cf.name)
        
        self.assertEquals(None, c['test']['required'])
        self.assertTrue(c['test']['blacklist'][0].match)
        self.assertEquals(None, c['test']['whitelist'])
        self.assertEquals([0], c['test']['exit_codes'])
        self.assertEquals('root', c['test']['email_to'])
        self.assertEquals(None, c['test']['email_from'])
        self.assertEquals(4096, c['test']['email_maxsize'])
        self.assertEquals(False, c['test']['email_success'])
        self.assertEquals('/usr/lib/sendmail', c['test']['email_sendmail'])
        self.assertEquals(None, c['test']['logfile'])

        self.assertEquals([], get_extra_values(c))

    def test_extra_settings(self):
        '''Should fail if there are extra configuration settings'''
        cf = NamedTemporaryFile()
        cf.write('[test]\n')
        cf.write('a=1\n')
        cf.write('b=2\n')
        cf.seek(0)

        self.assertRaisesError(cronwatch.Error,
                'unknown setting in configuration: a',
                cronwatch.read_config, cf.name)

    def test_configuration_error(self):
        '''TODO'''

    def test_regexes(self):
        '''Should verify and normalize the regular expresions'''
        for r in ['required', 'whitelist', 'blacklist']:
            cf = NamedTemporaryFile()
            cf.write('[test]\n')
            cf.write('%s = val\n' % r)
            cf.seek(0)
            
            c = cronwatch.read_config(cf.name)
            self.assertTrue(c['test'][r][0].match)

   #def test_default_configfile(self):
    #    '''Should read the main configuration file if it exists'''
    #    cf = NamedTemporaryFile()
    #    cf.write('[job]\n')
    #    cf.write('exit_codes=10, 101\n')
    #    cf.seek(0)

    #    cronwatch.CONFIGFILE = cf.name

    #    c = cronwatch.read_config()

    #    #self.assertEquals([10, 101], c['job']exit_codes)

#    def test_configfile_command_line(self):
#        '''Should read an alternate config file'''
#        cf = NamedTemporaryFile()
#        cf.write('[fake]\n')
#        cf.write('required = stuff\n')
#        cf.seek(0)
#
#        cronwatch.CONFIGFILE = cf.name
#
#        cf2 = NamedTemporaryFile()
#        cf2.write('[job]\n')
#        cf2.write('exit_codes = 1\n')
#        cf2.seek(0)
#
#        c = cronwatch.read_config(config_file = cf2.name)
#
#        self.assertFalse(c.has_section('fake'))
#        self.assertEquals(1, c.job.exit_codes)
#
#    def test_require_configfile(self):
#        '''Should raise an exception if the config file doesn't exist'''
#        self.assertRaises(IOError, cronwatch.read_config, 
#                          'this_is_not_a_file.forsure')

class TestCallSendmail(TestBase):
    '''Test the call_sendmail() function'''
    def setUp(self):
        self.tempdir = mkdtemp()

    def tearDown(self):
        rmtree(self.tempdir)

    def test_simple(self):
        '''Should run sendmail and pass the file in as input'''
        out = os.path.join(self.tempdir, 'sendmailoutput')
        cronwatch.call_sendmail(['./test_script.sh', 'sendmail', out], 'output')

        o = open(out).read()
        self.assertEquals('output', o)

    def test_sendmail_error_running(self):
        '''Should raise an exception when sendmail can't be run'''
        self.assertRaisesError(cronwatch.Error,
                'could not run sendmail: ./this_is_not_a_script.forsure: ' + 
                '[Errno 2] No such file or directory',
                cronwatch.call_sendmail, ['./this_is_not_a_script.forsure'], 
                'output')

    def test_sendmail_exitcode(self):
        '''Should raise an exception if there's a non-standard exit code'''
        self.assertRaisesError(cronwatch.Error,
                'sendmail returned exit code 10: ' + 
                'stdout\nstderr\nstdout again\n',
                cronwatch.call_sendmail, ['./test_script.sh', 'simple'],
                'outputtmp')

class TestSendMail(TestBase):
    '''Test the send_mail() function

       send_mail(sendmail, to_addr, subject, text, from_addr = None,
                 html = None)
    '''
    def call_sendmail(self, *args):
        self.args = args

    def setUp(self):
        self.args = None
        self.old_call_sendmail = cronwatch.call_sendmail
        cronwatch.call_sendmail = self.call_sendmail

    def tearDown(self):
        cronwatch.call_sendmail = self.old_call_sendmail

    def test_call_sendmail(self):
        '''Should parse the sendmail command line and pass it to
           call_sendmail'''
        cronwatch.send_mail('''/usr/bin/sendmail 'this is a "test"' "*"''',
                            'to', 'subject', 'text')

        self.assertEquals(self.args[0], ['/usr/bin/sendmail', 
                                         'this is a "test"', '*'])

    def test_formatted_mail(self):
        '''Should prepare an e-mail message'''
        cronwatch.send_mail('sendmail', 'to@domain.com', 'my subject',
                            'e-mail body\nmore text', 'from@domain.com')
        
        lines = self.args[1].split('\n')
        self.assertEquals('Content-Type: text/plain; charset="us-ascii"',
                          lines[0])
        self.assertEquals('To: to@domain.com', lines[3])
        self.assertEquals('From: from@domain.com', lines[4])
        self.assertEquals('Subject: my subject', lines[5])
        self.assertEquals('', lines[6])
        self.assertEquals('e-mail body', lines[7])
        self.assertEquals('more text', lines[8])

    def test_auto_from(self):
        '''Should auto generate the from user'''
        cronwatch.send_mail('sendmail', 'to', 'subject', 'text')
        from_addr = '%s@%s' % (getuser(), getfqdn(gethostname()))
        lines = self.args[1].split('\n')
        self.assertEquals('From: %s' % from_addr, lines[4])

    def test_html(self):
        '''Should create a html part'''
        cronwatch.send_mail('sendmail', 'to', 'subject', 'text', html = 'html')
        
        lines = self.args[1].split('\n')
        self.assertEquals('Content-Type: multipart/alternative',
                          lines[0].split(';')[0])
        self.assertEquals('', lines[5])
        self.assertEquals('Content-Type: text/plain; charset="us-ascii"',
                          lines[7])
        self.assertEquals('text', lines[11])
        self.assertEquals('Content-Type: text/html; charset="us-ascii"',
                          lines[13])
        self.assertEquals('html', lines[17])


class TestWatch(TestBase):
    '''Test the watch() function'''

if __name__ == '__main__':
    unittest.main()
