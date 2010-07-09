#!/usr/bin/python
# $Id$
# vim:ft=python:sw=4:sta:et
#
# test_simpleconfig.py - Unit tests for simpleconfig
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
from test_base import TestBase
from simpleconfig import *

###############################################################################
# SimpleConfig Tests
###############################################################################
class TestSimpleConfigSetting(TestBase):
    '''Tests for the SimpleConfigSetting class'''

    def test_set_get(self):
        '''Should allow us to set and get the value'''
        s = SimpleConfigSetting()
        self.assertEqual(None, s.get())
        s.set('value')
        self.assertEqual('value', s.get())

    def test_constructor(self):
        '''Should allow the constructor to set the value'''
        s = SimpleConfigSetting('value')
        self.assertEqual('value', s.get())

    def test_auto_value(self):
        '''Should return an automatic value'''
        self.assertEqual(None, SimpleConfigSetting.auto_value('nOne'))
        self.assertEqual(None, SimpleConfigSetting.auto_value('nUll'))
        self.assertEqual(-1, SimpleConfigSetting.auto_value('-1'))
        self.assertEqual(0, SimpleConfigSetting.auto_value('0'))
        self.assertEqual(1234567890,
                         SimpleConfigSetting.auto_value('1234567890'))
        self.assertEqual(True, SimpleConfigSetting.auto_value('tRue'))
        self.assertEqual(True, SimpleConfigSetting.auto_value('yEs'))
        self.assertEqual(True, SimpleConfigSetting.auto_value('oN'))
        self.assertEqual(False, SimpleConfigSetting.auto_value('fAlse'))
        self.assertEqual(False, SimpleConfigSetting.auto_value('nO'))
        self.assertEqual(False, SimpleConfigSetting.auto_value('oFf'))

        # Check to make sure we're checking the whole string
        self.assertEqual('none1', SimpleConfigSetting.auto_value('none1'))
        self.assertEqual('1none', SimpleConfigSetting.auto_value('1none'))
        self.assertEqual('a-1', SimpleConfigSetting.auto_value('a-1'))
        self.assertEqual('-1a', SimpleConfigSetting.auto_value('-1a'))
        self.assertEqual('true1', SimpleConfigSetting.auto_value('true1'))
        self.assertEqual('1true', SimpleConfigSetting.auto_value('1true'))

    def test_set_auto(self):
        '''Should set value automatically and set the raw value as well'''
        s = SimpleConfigSetting()
        s.set('1')
        self.assertEquals(1, s.get())
        self.assertEquals('1', s.get(raw = True))
        
        s.set(1)
        self.assertEquals(1, s.get())
        self.assertEquals(1, s.get(raw = True))

    def test_no_auto(self):
        '''Should not set a value automatically'''
        s = SimpleConfigSetting()
        s.set('1', auto_value = False)
        self.assertEquals('1', s.get())

        s = SimpleConfigSetting('1', auto_value = False)
        self.assertEquals('1', s.get())

class TestSimpleConfigSection(TestBase):
    '''Tests for the SimpleClassSection class'''

    def test_get_set(self):
        '''Should allow getting and setting via methods'''
        s = SimpleConfigSection()
        
        s.set('setting', '1')
        self.assertEquals(1, s.get('setting'))
        self.assertEquals('1', s.get('setting', raw = True))
        
        s.set('setting', '1', auto_value = False)
        self.assertEquals('1', s.get('setting'))

    def test_constructor(self):
        '''Should allow settings in constructor'''
        s = SimpleConfigSection({'a': '1', 'b': '2'})
        self.assertEquals(1, s.get('a'))
        self.assertEquals(2, s.get('b'))
        
        s = SimpleConfigSection({'a': '1'}, auto_value = False)
        self.assertEquals('1', s.get('a'))

    def test_invalid_setting(self):
        '''Should throw an exception is the setting is not known'''
        self.assertRaisesError(SettingError, 
                               'invalid setting wrong',
                                SimpleConfigSection().get, 'wrong')

    def test_getattr(self):
        '''Should implement section.setting behavior'''
        s = SimpleConfigSection({'a': '1', 'b': '2'})
        self.assertEquals(1, s.a)
        self.assertEquals(2, s.b)

    def test_setattr(self):
        '''Should implement section.setting = value behavior'''
        s = SimpleConfigSection()
        s.a = '1'
        self.assertEquals(1, s.get('a'))


if __name__ == '__main__':
    unittest.main()
