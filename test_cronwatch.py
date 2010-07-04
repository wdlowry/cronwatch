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


if __name__ == '__main__':
    unittest.main()
