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

if __name__ == '__main__':
    unittest.main()
