#!/usr/bin/python
# $Id$
# vim:ft=python:sw=4:sta:et
#
# test_cronwatch.py - Unit tests for cronwatch
# Copyright (C) 2011 David Lowry  < wdlowry at gmail dot com >
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
from test_base import *
from validate import VdtTypeError, VdtValueError
from configobj import get_extra_values
from getpass import getuser
from datetime import datetime

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

class TestLineSearch(TestBase):
    def test_match(self):
        '''Should tell if a list of regular expressions matches a line and
           which ones'''
        r = cronwatch.line_search('test', [re.compile('t'),
                                           re.compile('e'),
                                           re.compile('1')])
        self.assertEquals((True, ['t', 'e']), r)
        
    def test_no_match(self):
        '''Should return an empty list if there were no matches'''
        r = cronwatch.line_search('test', [re.compile('1'),
                                           re.compile('2'),
                                           re.compile('3')])
        self.assertEquals((False, []), r)

    def test_all(self):
        '''Should return a list of just the ones that were found'''
        r = cronwatch.line_search('test', [re.compile('t'),
                                           re.compile('e'),
                                           re.compile('s')], find_all = True)
        self.assertEquals((True, ['t', 'e', 's']), r)
        
        r = cronwatch.line_search('test', [re.compile('t'),
                                           re.compile('2'),
                                           re.compile('3')], find_all = True)
        self.assertEquals((False, ['t']), r)

class TestIsReadableFile(TestBase):
    def test_file(self):
        '''Should return a filename'''
        self.assertEquals('test_file.txt',
                cronwatch.is_readable_file('test_file.txt'))
    
    def test_no_file(self):
        '''Should raise a validation error'''
        self.assertRaisesError(cronwatch.VdtValueMsgError,
                """could not read file: [Errno 2] No such file or directory: 'not_a_file.txt'""",
               cronwatch.is_readable_file, 'not_a_file.txt')


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
            self.assertEquals([], c[s]['required'])
            self.assertEquals(None, c[s]['whitelist'])
            self.assertEquals([], c[s]['blacklist'])
            self.assertEquals([0], c[s]['exit_codes'])
            self.assertEquals(None, c[s]['preamble_file'])
            self.assertEquals(None, c[s]['email_to'])
            self.assertEquals(None, c[s]['email_from'])
            self.assertEquals(102400, c[s]['email_maxsize'])
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
    
    def test_preamble_file(self):
        '''Should verify the preamble_file'''
        cf = self.config('[test1]\npreamble_file = test_file.txt')
        c = cronwatch.read_config(cf.name)
        self.assertEquals('test_file.txt', c['test1']['preamble_file'])

        cf = self.config('[test1]\npreamble_file = not_a_file.txt')
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
        self.register_cleanup(self.tempdir)

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
        while lines[0].find('Content-Type') == -1: lines.pop(0)
        self.assertEquals('Content-Type: multipart/alternative',
                          lines[0].split(';')[0])
        lines.pop(0)
        
        while lines[0].find('Content-Type') == -1: lines.pop(0)
        self.assertEquals('Content-Type: text/plain; charset="us-ascii"',
                          lines[0])
        lines.pop(0)

        while lines[0].find('Content-Type') == -1: lines.pop(0)
        self.assertEquals('Content-Type: text/html; charset="us-ascii"',
                          lines[0])

class TestGetNow(TestBase):
    def test_get_now(self):
        '''Should return a formatted string for right now'''
        # I'm not sure this is always going to work
        self.assertEquals(datetime.now().strftime('%c'), cronwatch.get_now())

class TestWatch(TestBase):
    '''Test the watch() function'''
    def setUp(self):
        self.time = 0
    
        self.old_config = cronwatch.CONFIGFILE
        cronwatch.CONFIGFILE = 'this_is_not_a_file.forsure'

        self.old_send_mail = cronwatch.send_mail
        cronwatch.send_mail = self.send_mail
        self.old_get_now = cronwatch.get_now
        cronwatch.get_now = self.get_now

    def tearDown(self):
        cronwatch.CONFIGFILE = self.old_config
        cronwatch.send_mail = self.old_send_mail
        cronwatch.get_now = self.old_get_now

    def send_mail(self, sendmail, subject, text, to_addr = None, 
                  from_addr = None, html = None):
        self.send = True
        self.send_sendmail = sendmail
        self.send_to = to_addr
        self.send_subject = subject
        self.send_text = text.split('\n')
        self.send_text_raw = text
        self.send_from = from_addr

    def get_now(self):
        t = self.time
        self.time += 1
        return 'time%i' % t

    def watch(self, conf, cmd, *args, **kwargs):
        self.send = False

        cf = NamedTemporaryFile()
        cf.write('[job]\n%s' % conf)
        cf.seek(0)
        
        tf = NamedTemporaryFile()

        self.cmd_line = ['./test_script.sh', cmd, tf.name] + list(args)
        tag = 'job'
        if kwargs.has_key('tag'): tag = kwargs['tag']
        
        force = False
        if kwargs.has_key('force_blacklist'): force = kwargs['force_blacklist']
        cronwatch.watch(self.cmd_line, config = cf.name, tag = tag, 
                        force_blacklist = force)
        self.cmd_line = ' '.join(self.cmd_line)

        return tf.read()
    
    def test_no_output(self):
        '''Should run the executable with arguments and just quit'''
        o = self.watch('', 'quiet', 'arg')
        self.assertEquals('quiet arg\n', o)
        self.assertFalse(self.send)

    def test_email_success(self):
        '''Should send an e-mail if the email_success flag is set'''
        self.watch('email_success = on', 'quiet', 'arg')
        self.assertTrue(self.send)

    def test_no_tag(self):
        '''Should use the default section if the tag doesn't exist in the 
           config'''
        self.watch('[_default_]\nemail_success = on\n',
                   'quiet', 'arg', tag = 'doesnotexist')
        self.assertTrue(self.send)

    def test_auto_tag(self):
        '''Should figure out the tag from the script name by default'''
        self.watch('[test_script.sh]\nemail_success = on\n',
                   'quiet', 'arg', tag = None)
        self.assertTrue(self.send)

    def test_email_subject(self):
        '''Should set the e-mail subject'''
        self.watch('email_success = on', 'quiet', 'arg')
        self.assertEquals('cronwatch <%s> %s' % 
                          (get_user_hostname(), self.cmd_line),
                          self.send_subject)
    
    def test_email_to(self):
        '''Should set the e-mail to address'''
        self.watch('email_success = on', 'quiet', 'arg')
        self.assertEquals(None, self.send_to)

        self.watch('email_success = on\nemail_to = testuser', 'quiet', 'arg')
        self.assertEquals('testuser', self.send_to)

    def test_email_from(self):
        '''Should set the e-mail from address'''
        self.watch('email_success = on', 'quiet', 'arg')
        self.assertEquals(None, self.send_from)

        self.watch('email_success = on\nemail_from = testuser', 'quiet', 'arg')
        self.assertEquals('testuser', self.send_from)

    def test_email_sendmail(self):
        '''Should set the sendmail path'''
        self.watch('email_success = on', 'quiet', 'arg')
        self.assertEquals('/usr/lib/sendmail', self.send_sendmail)

        self.watch('email_success = on\nemail_sendmail = sm', 'quiet', 'arg')
        self.assertEquals('sm', self.send_sendmail)

    def test_email_body(self):
        '''Should format the body correctly'''
        self.watch('email_success = on', 'quiet', 'arg')
        self.assertEquals('The following command line executed successfully:',
                          self.send_text[0])
        self.assertEquals(self.cmd_line, self.send_text[1])
        self.assertEquals('', self.send_text[2])
        self.assertEquals('Started execution at:  time0', self.send_text[3])
        self.assertEquals('Finished execution at: time1', self.send_text[4])
        self.assertEquals('Exit code: 0', self.send_text[5])
        self.assertEquals('', self.send_text[6])
        self.assertEquals('Output:', self.send_text[7])
        self.assertEquals('  No output', self.send_text[8])

    def test_email_output(self):
        '''Should append the output to the end of the file'''
        self.watch('email_success = on', 'out', 'a', 'b')
        self.assertEquals('Output:', self.send_text[7])
        self.assertEquals('  a', self.send_text[8])
        self.assertEquals('  b', self.send_text[9])
        self.assertEquals('[EOF]', self.send_text[10])

    def test_preamble_text(self):
        '''Should add the pramble to the output'''
        self.watch('email_success = on\npreamble_file = test_file.txt', 'out', 
                  'a', 'b')
        self.assertEquals('', self.send_text[6])
        self.assertEquals('This is sample text.', self.send_text[7])
        self.assertEquals('', self.send_text[8])
        self.assertEquals('Output:', self.send_text[9])
    
    def test_email_maxsize(self):
        '''Should truncate the e-mail output if it's too big'''
        self.watch('email_success = on\nemail_maxsize = -1', 'out', 'a' * 4097)
        self.assertEquals('  ' + 'a' * 4097, self.send_text[8])
        self.assertEquals('[EOF]', self.send_text[9])
        
        self.watch('email_success = on\nemail_maxsize = -1', 'out', 'line1')
        size = len(self.send_text_raw) - len('[EOF]')
        
        self.watch('email_success = on\nemail_maxsize = %i' % size,
                   'out', 'line1')
        self.assertEquals('  line1', self.send_text[8])
        self.assertEquals('[EOF]', self.send_text[9])

        self.watch('email_success = on\nemail_maxsize = %i' % (size - 1),
                   'out', 'line1')
        self.assertEquals('  line1', self.send_text[8])
        self.assertEquals('[Output truncated]', self.send_text[9])

    def test_email_error(self):
        '''Should change the status line if there were errors in execution'''
        self.watch('exit_codes = 1, 2', 'exit', '3')
        self.assertEquals('The following command line executed with errors:',
                          self.send_text[0])

    def test_exit_codes(self):
        '''Should send a mail if the exit code doesn't match'''
        self.watch('exit_codes = 1, 2', 'exit', '1')
        self.assertFalse(self.send)
        
        self.watch('exit_codes = 1, 2', 'exit', '2')
        self.assertFalse(self.send)

        self.watch('exit_codes = 1, 2', 'exit', '3')
        self.assertEquals('  * Exit code (3) is not a valid exit code', 
                           self.send_text[8])

    def test_required(self):
        '''Should search for required output'''
        self.watch('required = req, line', 'out', 'line1', 'req', 'line3')
        self.assertFalse(self.send)

        self.watch('required = req, more', 'out', 'line1', 'line2', 'line3')
        self.assertEquals('  * Required output missing (more)', 
                          self.send_text[8])
        self.assertEquals('  * Required output missing (req)', 
                          self.send_text[9])
    
    def test_whitelist(self):
        '''Should cause an error if there is non-whitelist output'''
        self.watch('whitelist = white, bright', 
                   'out', 'whitelight', 'brightlight', 'whitebright')
        self.assertFalse(self.send)

        self.watch('whitelist = white, bright',
                   'out', 'whitelight', 'black', 'whitebright')
        self.assertEquals('  * Output not matched by whitelist ' +
                          '(denoted by "*" in output)', self.send_text[8])
        self.assertEquals('  whitelight', self.send_text[12])
        self.assertEquals('* black', self.send_text[13])
        self.assertEquals('  whitebright', self.send_text[14])
        self.assertEquals('[EOF]', self.send_text[15])

    def test_blacklist(self):
        '''Should cause an error if there is blacklist output'''
        self.watch('blacklist = black, dark', 'out', 'line1', 'line2', 'line3')
        self.assertFalse(self.send)

        self.watch('blacklist = black, dark', 'out', 'black', 'dark', 'line3')
        self.assertEquals('  * Output matched by blacklist (black) ' +
                          '(denoted by "!" in output)',
                          self.send_text[8])
        self.assertEquals('  * Output matched by blacklist (dark) ' +
                          '(denoted by "!" in output)', 
                          self.send_text[9])
        self.assertEquals('! black', self.send_text[13])
        self.assertEquals('! dark', self.send_text[14])
        self.assertEquals('  line3', self.send_text[15])

    def test_default_blacklist(self):
        '''Should create a blacklist if none of the regex options are
           specified'''
        self.watch('', 'out', 'line1', 'line2', force_blacklist = True)
        self.assertEquals('  * Output matched by blacklist (.*) ' + 
                          '(denoted by "!" in output)',
                          self.send_text[8])
        self.assertEquals('! line1', self.send_text[12])
        self.assertEquals('! line2', self.send_text[13])

    def test_logfile(self):
        '''Should open and append to a log file'''
        logfile = NamedTemporaryFile()
        logfile.write('line1\n')
        logfile.seek(0)

        self.watch(('logfile = %s\nemail_maxsize = 1\n' + 
                   'preamble_file = test_file.txt') % logfile.name, 
                   'out', 'line1', 'line2')
        o = logfile.read().split('\n')

        self.assertEquals('line1', o[0])
        self.assertEquals('The following command line executed successfully:',
                          o[1])
        self.assertEquals(self.cmd_line, o[2])
        self.assertEquals('', o[3])
        self.assertEquals('Started execution at:  time0', o[4])
        self.assertEquals('Finished execution at: time1', o[5])
        self.assertEquals('Exit code: 0', o[6])
        self.assertEquals('', o[7])
        self.assertEquals('This is sample text.', o[8])
        self.assertEquals('', o[9])
        self.assertEquals('Output:', o[10])
        self.assertEquals('  line1', o[11])
        self.assertEquals('  line2', o[12])
        self.assertEquals('[EOF]', o[13])
        self.assertEquals('', o[14])
        self.assertEquals('', o[15])
    
    def test_logfile_empty_output(self):
        '''Should open and write to a log file even if there is no output'''
        logfile = NamedTemporaryFile()

        self.watch('logfile = %s\nemail_maxsize = 1' % logfile.name, 'out')
        o = logfile.read().split('\n')

        self.assertEquals('The following command line executed successfully:',
                          o[0])
        self.assertEquals(self.cmd_line, o[1])
        self.assertEquals('', o[2])
        self.assertEquals('Started execution at:  time0', o[3])
        self.assertEquals('Finished execution at: time1', o[4])
        self.assertEquals('Exit code: 0', o[5])
        self.assertEquals('', o[6])
        self.assertEquals('Output:', o[7])
        self.assertEquals('  No output', o[8])
        self.assertEquals('', o[9])
        self.assertEquals('', o[10])

    def test_logfile_name(self):
        '''Should format the name of the logfile correctly'''
        d = mkdtemp()
        self.register_cleanup(d)

        logfile = os.path.join(d, 'job_%Y')
        self.watch('logfile = %s\nemail_maxsize = 1' % logfile, 
                   'out', 'line1', 'line2')

        logfile = os.path.join(d, datetime.now().strftime('job_%Y'))
        o = open(logfile).read().split('\n')
        self.assertEquals('  line1', o[8])


if __name__ == '__main__':
    unittest.main()
