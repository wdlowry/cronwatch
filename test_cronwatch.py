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
import re
from tempfile import NamedTemporaryFile, TemporaryFile, mkdtemp, mkstemp
from StringIO import StringIO
from shutil import rmtree
from test_base import *
from validate import VdtTypeError, VdtValueError
from configobj import get_extra_values
from getpass import getuser


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

class TestSearchFile(TestBase):
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
        self.write('one\ntwo\nthree\n1\n2\n3')
        r = cronwatch.filter_text({'first': [re.compile('one')]}, self.tmp)
        self.assertEqual({'first': {'one': [1]}}, r)

    def test_complex(self):
        '''Should find all the lines with the search expressions'''
        self.write('one\ntwo\nthree\n1\n2\n3')
        r1 = re.compile('one')
        r2 = re.compile('two')
        r3 = re.compile('[1-3]')
        r4 = re.compile('not')
        rx = {'1': [r1], '2': [r2, r3], '3': [r1, r4], '4': [r4], '5': []}
        r = cronwatch.filter_text(rx, self.tmp)
        self.assertEqual({'1': {'one': [1]},
                          '2': {'two': [2], '[1-3]': [4, 5, 6]},
                          '3': {'one': [1], 'not': []},
                          '4': {'not': []},
                          '5': {}}, r)

    def test_not_found(self):
        '''Should only mark lines that match none of the search expressions'''
        self.write('one\ntwo\nthree\n1\n2\n3')
        rx = {'1': [re.compile('[1-3]')]}
        r = cronwatch.filter_text(rx, self.tmp, not_found = ['1'])
        self.assertEqual({'1': [1, 2, 3]}, r)

    def test_not_found_complex(self):
        '''Should only mark lines that match none of the search expressions'''
        self.write('one\ntwo\nthree\n1\n2\n3')
        r1 = re.compile('one')
        r2 = re.compile('two')
        r3 = re.compile('[1-3]')
        r4 = re.compile('not')
        rx = {'1': [r1], '2': [r2, r3], '3': [r1, r4], '4': [r4], '5': []}
        r = cronwatch.filter_text(rx, self.tmp,
                                  not_found = ['1', '2', '3', '4', '5'])
        self.assertEqual({'1': [2, 3, 4, 5, 6],
                          '2': [1, 3],
                          '3': [2, 3, 4, 5, 6],
                          '4': [1, 2, 3, 4, 5, 6],
                          '5': []}, r)

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

class TestReadConfig(TestBase):
    '''Test the read_config() function'''

    def setUp(self):
        self.old_config = cronwatch.CONFIGFILE
        cronwatch.CONFIGFILE = 'this_is_not_a_file.forsure'

    def tearDown(self):
        cronwatch.CONFIGFILE = self.old_config

    def config(self, text):
        '''Create a NamedTemporaryFile and return the object'''
        cf = NamedTemporaryFile()
        cf.write(text)
        cf.seek(0)
        return cf

    def test_defaults(self):
        '''Should set defaults if no config is found'''
        cf = self.config('[test]');
        c = cronwatch.read_config(cf.name)

        for s in ['test', '_default_']:
            self.assertEquals(None, c[s]['required'])
            self.assertEquals(None, c[s]['whitelist'])
            self.assertEquals(None, c[s]['blacklist'])
            self.assertEquals([0], c[s]['exit_codes'])
            self.assertEquals(None, c[s]['email_to'])
            self.assertEquals(None, c[s]['email_from'])
            self.assertEquals(4096, c[s]['email_maxsize'])
            self.assertEquals(False, c[s]['email_success'])
            self.assertEquals('/usr/lib/sendmail', c[s]['email_sendmail'])
            self.assertEquals(None, c[s]['logfile'])

        self.assertEquals([], get_extra_values(c))

    def test_parse_error(self):
        '''Should raise an error when the config file is bad'''
        cf = self.config('[test')
        self.assertRaisesError(cronwatch.Error,
                'could not read %s: Invalid line at line "1".' % cf.name, 
                cronwatch.read_config, cf.name)

    def test_extra_settings(self):
        '''Should fail if there are extra configuration settings'''
        cf = self.config('''[test]
                            a=1
                            b=2''')

        self.assertRaisesError(cronwatch.Error,
                'unknown setting in configuration: a',
                cronwatch.read_config, cf.name)

    def test_validation_error(self):
        '''Should raise an Exception with a helpful error message'''
        cf = self.config('[test]\nrequired = (')
        self.assertRaisesError(cronwatch.Error,
                'configuration error for test.required: ' + 
                'invalid regular expression: (: unbalanced parenthesis',
                cronwatch.read_config, cf.name)

    def test_regexes(self):
        '''Should verify and normalize the regular expresions'''
        for r in ['required', 'whitelist', 'blacklist']:
            cf = self.config('[test]\n%s = val'  % r)
            c = cronwatch.read_config(cf.name)
            self.assertTrue(c['test'][r][0].match)
            
            cf = self.config('[test]\n%s = (')
            self.assertRaises(cronwatch.Error, cronwatch.read_config, cf.name)

    def test_exit_codes(self):
        '''Should verify and normalize the exit codes'''
        cf = self.config('[test]\nexit_codes = 1')
        c = cronwatch.read_config(cf.name)
        self.assertEquals([1], c['test']['exit_codes'])
        
        cf = self.config('[test]\nexit_codes = 1, 2')
        c = cronwatch.read_config(cf.name)
        self.assertEquals([1, 2], c['test']['exit_codes'])

        cf = self.config('[test]\nexit_codes = a')
        self.assertRaises(cronwatch.Error, cronwatch.read_config, cf.name)

    def test_emails(self):
        '''Should verify and normalize the email addresses'''
        cf = self.config('[test]\nemail_to = default\nemail_from = me@dom.com')
        c = cronwatch.read_config(cf.name)
        self.assertEquals('default', c['test']['email_to'])
        self.assertEquals('me@dom.com', c['test']['email_from'])
        
        cf = self.config('[test]\nemail_to = me,too')
        self.assertRaises(cronwatch.Error, cronwatch.read_config, cf.name)

    def test_email_maxsize(self):
        '''Should verify and normalize the email maximum size'''
        cf = self.config('[test]\nemail_maxsize = -1')
        c = cronwatch.read_config(cf.name)
        self.assertEquals(-1, c['test']['email_maxsize'])

        cf = self.config('[test]\nemail_maxsize = -2')
        self.assertRaises(cronwatch.Error, cronwatch.read_config, cf.name)

    def test_email_success(self):
        '''Should verify and normalize the email_sucess parameter'''
        cf = self.config('[test1]\nemail_success = on\n' +
                         '[test2]\nemail_success = off')
        c = cronwatch.read_config(cf.name)
        self.assertEquals(True, c['test1']['email_success'])
        self.assertEquals(False, c['test2']['email_success'])

        cf = self.config('[test]\nemail_success = 1, 2')
        self.assertRaises(cronwatch.Error, cronwatch.read_config, cf.name)

    def test_paths(self):
        '''Should verify the path variables get set'''
        cf = self.config('[test]\nemail_sendmail = /l/sendmail -t"s 1"\n' +
                         'logfile = file%var%')
        c = cronwatch.read_config(cf.name)
        self.assertEquals('/l/sendmail -t"s 1"', c['test']['email_sendmail'])
        self.assertEquals('file%var%', c['test']['logfile'])

    def test_default_configfile(self):
        '''Should read the main configuration file if it exists'''
        cf = self.config('[test]\nexit_codes = 1')
        cronwatch.CONFIGFILE = cf.name
        c = cronwatch.read_config()
        self.assertEquals([1], c['test']['exit_codes'])

    def test_configfile_command_line(self):
        '''Should read an alternate config file'''
        cf = self.config('[test]\nexit_codes = 2') #
        cronwatch.CONFIGFILE = cf.name
        cf2 = self.config('[test]\nexit_codes = 1') #
        c = cronwatch.read_config(config_file = cf2.name)

        self.assertEquals([1], c['test']['exit_codes'])

    def test_require_configfile(self):
        '''Should raise an exception if the config file doesn't exist'''
        self.assertRaisesError(cronwatch.Error,
                'Config file not found: "this_is_not_a_file.forsure".',
                cronwatch.read_config, 'this_is_not_a_file.forsure')

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
                            'subject', 'text', 'to')

        self.assertEquals(self.args[0], ['/usr/bin/sendmail', 
                                         'this is a "test"', '*', 'to'])

    def test_formatted_mail(self):
        '''Should prepare an e-mail message'''
        cronwatch.send_mail('sendmail', 'my subject',
                            'e-mail body\nmore text', 'to@domain.com',
                            'from@domain.com')
        
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
        '''Should auto generate the from address'''
        cronwatch.send_mail('sendmail', 'subject', 'text', 'to')
        lines = self.args[1].split('\n')
        self.assertEquals('From: %s' % get_user_hostname(), lines[4])
    
    def test_auto_to(self):
        '''Should auto generate the to address'''
        cronwatch.send_mail('sendmail', 'subject', 'text')
        lines = self.args[1].split('\n')
        self.assertEquals('To: %s' % getuser(), lines[3])

    def test_html(self):
        '''Should create a html part'''
        cronwatch.send_mail('sendmail', 'subject', 'text', html = 'html')
        
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
    
    def setUp(self):
        self.tempfile = mkstemp()
        os.close(self.tempfile[0])
        self.tempfile = self.tempfile[1]

        self.cf = NamedTemporaryFile()

        self.old_config = cronwatch.CONFIGFILE
        cronwatch.CONFIGFILE = 'this_is_not_a_file.forsure'

        self.send = False
        self.old_send_mail = cronwatch.send_mail
        cronwatch.send_mail = self.send_mail

    def tearDown(self):
        os.remove(self.tempfile)

        self.cf.close()

        cronwatch.CONFIGFILE = self.old_config
        cronwatch.send_mail = self.old_send_mail

    def send_mail(self, sendmail, subject, text, to_addr = None, 
                  from_addr = None, html = None):

        self.send = True
        self.send_sendmail = sendmail
        self.send_to = to_addr
        self.send_subject = subject
        self.send_text = text.split('\n')
        self.send_from = from_addr

    def conf(self, text):
        '''Write the config file'''
        self.cf.write('[job]\n')
        self.cf.write(text)
        self.cf.seek(0)
    
    def watch(self, cmd, *args):
        self.cmd_line = ['./test_script.sh', cmd, self.tempfile] + list(args)
        cronwatch.watch(self.cmd_line, config = self.cf.name, tag = 'job')
        self.cmd_line = ' '.join(self.cmd_line)
    
    def test_simple(self):
        '''Should run the executable with arguments and just quit'''
        self.watch('quiet', 'arg')
        o = [l.rstrip() for l in open(self.tempfile).readlines()]
        self.assertEquals('quiet arg', o[0])
        self.assertFalse(self.send)

    def test_email_subject(self):
        '''Should set the e-mail subject'''
        self.watch('exit', '1')
        self.assertEquals('cronwatch <%s> %s' % 
                          (get_user_hostname(), self.cmd_line),
                          self.send_subject)
    
    def test_email_to(self):
        '''Should set the e-mail to address'''
        self.watch('exit', '1')
        self.assertEquals(None, self.send_to)

        self.conf('email_to = testuser')
        self.watch('exit', '1')
        self.assertEquals('testuser', self.send_to)

    def test_email_from(self):
        '''Should set the e-mail from address'''
        self.watch('exit', '1')
        self.assertEquals(None, self.send_from)

        self.conf('email_from = testuser')
        self.watch('exit', '1')
        self.assertEquals('testuser', self.send_from)

    def test_email_sendmail(self):
        '''Should set the sendmail path'''
        self.watch('exit', '1')
        self.assertEquals('/usr/lib/sendmail', self.send_sendmail)

        self.conf('email_sendmail = sm')
        self.watch('exit', '1')
        self.assertEquals('sm', self.send_sendmail)

    def test_email_body(self):
        '''Should say if the job completed successfully'''
        self.watch('exit', '1')
        self.assertEquals('The following command line executed with an error:',
                          self.send_text[0])
        self.assertEquals('    ' + self.cmd_line, self.send_text[1])
        self.assertEquals('', self.send_text[2])
        self.assertEquals('', self.send_text[3])
        self.assertEquals('Errors:', self.send_text[4])
    
    def test_exit_codes(self):
        '''Should send a mail if the exit code doesn't match'''
        self.conf('exit_codes = 1, 2')
        self.watch('exit', '1')
        self.assertFalse(self.send)
        
        self.conf('exit_codes = 1, 2')
        self.watch('exit', '2')
        self.assertFalse(self.send)

        self.conf('exit_codes = 1, 2')
        self.watch('exit', '3')
        self.assertEquals('    * Exit code (3) was not a valid exit code', 
                          self.send_text[5])

    def test_required(self):
        '''Should search for required output'''
        self.conf('required = req, line')
        self.watch('out', 'line1', 'req', 'line3')
        self.assertFalse(self.send)

        self.conf('required = req, more')
        self.watch('out', 'line1', 'line2', 'line3')
        self.assertEquals('    * Did not find required output (more)', 
                          self.send_text[5])
        self.assertEquals('    * Did not find required output (req)', 
                          self.send_text[6])
    
    #def test_whitelist(self):
    #    '''Should cause an error if there is non-whitelist output'''
    #    self.conf('whitelist = white, bright')
    #    self.watch('whiteout', 'whitelight', 'brightlight', 'whitebright')
    #    self.assertFalse(self.send)

    #    self.conf('whitelist = white, bright')
    #    self.watch('out', 'whitelight', 'black', 'whitebright')
    #    self.assertEquals('    * Found output not matched by whitelist', 
    #                      self.send_text[5])

    def test_blacklist(self):
        '''Should cause an error if there is blacklist output'''
        self.conf('blacklist = black, dark')
        self.watch('out', 'line1', 'line2', 'line3')
        self.assertFalse(self.send)

        self.conf('blacklist = black, dark')
        self.watch('out', 'black', 'dark', 'line3')
        self.assertEquals('    * Found blacklist output (black)', 
                          self.send_text[5])
        self.assertEquals('    * Found blacklist output (dark)', 
                          self.send_text[6])

#required output
#blacklist output
#whitelist output
#email_maxsize
#email_success
#logfile
# TAG HANDLING
                                                                                #
if __name__ == '__main__':
    unittest.main()
