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
import cronwatch
import tempfile

###############################################################################
# Test Helper Classes
###############################################################################
class TestBase(unittest.TestCase):
    '''Base class to add common idioms'''

    def setUp(self):
        unittest.TestCase.setUp(self)
        self._capture = False

    def assertRaisesError(self, exception, message, func, *args, **kwargs):
        '''Similar to assertRaises, but allows a check of the message
           variable of the exception.'''

        self.assertRaises(exception, func, *args, **kwargs)

        try:
            func(*args, **kwargs)
        except exception, e:
            self.assertEqual(str(e), message)
    
    def assertRaisesErrorMulti(self, exception, message, delimiter,
                               func, *args, **kwargs):
        '''Similar to assertRaisesError, but allows a check of just the 
           first line of the exception message.'''
        self.assertRaises(exception, func, *args, **kwargs)

        try:
            func(*args, **kwargs)
        except exception, e:
            self.assertEqual(str(e).split(delimiter)[0], message)

    def start_capture(self):
        '''Start stdout/stderr capture'''
        if self._capture:
            return

        self._capture = True
        self._stdout_str = StringIO.StringIO()
        self._stderr_str = StringIO.StringIO()
        self._stdout_old = sys.stdout
        self._stderr_old = sys.stderr
        sys.stdout = self._stdout_str
        sys.stderr = self._stderr_str

    def stop_capture(self):
        '''Stop stdout/stderr capture and return (stdout, strerr)'''
        if not self._capture:
            return
        self._capture = False
        stdout = self._stdout_str.getvalue()
        stderr = self._stderr_str.getvalue()
        sys.stdout = self._stdout_old
        sys.stderr = self._stderr_old
        self._stdout_str.close()
        self._stderr_str.close()

        return (stdout, stderr)

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
        self.tmp = tempfile.TemporaryFile()

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

class TestWatch(TestBase):
    '''Test the watch() function'''


if __name__ == '__main__':
    unittest.main()
