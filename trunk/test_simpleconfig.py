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
import StringIO

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

    def test_get_settings(self):
        '''Should return a list of setting names'''
        s = SimpleConfigSection({'a': '1', 'b': '2'})
        self.assertEquals(['a', 'b'], s.get_settings())

    def test_defaults(self):
        '''Should accept another section to set up defaults in the
           constructor'''
        s = SimpleConfigSection({'a': '1', 'b': '2'})
        c = SimpleConfigSection(defaults = s)
        self.assertEquals(c.get('a'), 1)
        self.assertEquals(c.get('b'), 2)

    def test_defaults_deep_copy(self):
        '''Should make a deep copy of the defaults so the main one doesn't get
           changed'''
        s = SimpleConfigSection({'c': [1, 2]})
        c = SimpleConfigSection(defaults = s)
        c.c.append(3)
        
        self.assertEquals(s.get('c'), [1, 2])
        self.assertEquals(c.get('c'), [1, 2, 3])


class TestSimpleConfig(TestBase):
    '''Tests for SimpleConfig class'''

    def test_add(self):
        '''Should add a section to the config'''
        s = SimpleConfig()

        self.assertEquals([], s.get_sections())
        s.add('two')
        sec = s.add('one')
        self.assertEquals(['one', 'two'], s.get_sections())
        self.assertTrue(isinstance(sec, SimpleConfigSection))

    def test_had(self):
        '''Should check if a section exists'''
        s = SimpleConfig()
        self.assertFalse(s.has('one'))
        s.add('one')
        self.assertTrue(s.has('one'))

    def test_duplicate_section(self):
        '''Should raise an exception if a section is added twice'''
        s = SimpleConfig()
        s.add('one')
        self.assertRaisesError(SectionError,
                               'section one already exists',
                               s.add, 'one')

    def test_get(self):
        '''Should return the specified section'''
        s = SimpleConfig()
        sec = s.add('one')
        sec.set('setting', '1')
        self.assertEquals(1, s.get('one').get('setting'))

    def test_invalid_section(self):
        '''Should throw an exception is the section is not known'''
        self.assertRaisesError(SectionError, 
                               'invalid section wrong',
                                SimpleConfig().get, 'wrong')

    def test_getattr(self):
        '''Should implement config.section behavior'''
        s = SimpleConfig()
        s.add('one')
        s.add('two')
        s.get('one').set('a', '1')
        s.get('two').set('b', '2')

        self.assertEquals(1, s.one.a)
        self.assertEquals(2, s.two.b)

    def test_getattr_autocreate(self):
        '''Should implement config.section.setting = value behavior'''
        s = SimpleConfig()
        s.one.a = '1'
        s.two.b = '2'
        
        self.assertEquals(1, s.one.a)
        self.assertEquals(2, s.two.b)

    def test_defaults(self):
        '''Should apply the default section settings other sections'''
        s = SimpleConfig()
        s.defaults.a = '1'
        s.defaults.b = '2'
        s.add('one')
        
        self.assertEquals(1, s.one.a)
        self.assertEquals(2, s.one.b)

    def test_readfp_parsing_error(self):
        '''Should raise an exception if something can't be understood'''
        f = StringIO.StringIO()
        f.write('#This is a comment\n')
        f.write('error\n')
        f.seek(0)

        self.assertRaisesError(ConfigError,
                'could not parse config file at line 2: error',
                SimpleConfig().readfp, f)
    
    def test_readfp_empty(self):
        '''Should create a mostly empty config'''
        s = SimpleConfig()
        s.readfp(StringIO.StringIO())
        self.assertEquals([], s.get_sections())

    def test_readfp_section(self):
        '''Should read in the section headers'''
        f = StringIO.StringIO()
        f.write('  \t  [  \t  section  one  \t  ]  \n')
        f.write('[two]')
        f.seek(0)

        s = SimpleConfig()
        s.readfp(f)

        self.assertEquals(['section  one', 'two'], s.get_sections())
        self.assertEquals([], s.get('section  one').get_settings())
        self.assertEquals([], s.two.get_settings())

    def test_readfp_simple(self):
        '''Should put a couple things in the main section'''
        f = StringIO.StringIO()
        f.write('[one]\n')
        f.write('  \t  a  \t  =  \t  a string  \t  \n')
        f.write('  \t  b b  \t  =  \t  1  \t  \n')
        f.seek(0)

        s = SimpleConfig()
        s.readfp(f)

        self.assertEquals(['one'], s.get_sections())
        self.assertEquals(['a', 'b b'], s.one.get_settings())
        self.assertEquals('a string', s.one.a)
        self.assertEquals(1, s.one.get('b b'))

    def test_readfp_missing_section(self):
        '''Should raise an error if the first section header is missing'''
        f = StringIO.StringIO()
        f.write('a=1\n')
        f.seek(0)

        s = SimpleConfig()
        self.assertRaisesError(ConfigError,
                'section header missing at line 1: a=1',
                s.readfp, f)

    def test_readfp_whitespace_comment(self):
        '''Should parse comments and blank lines correctly'''
        f = StringIO.StringIO()
        f.write('  \t \t  \n')
        f.write('# This is a comment\n')
        f.write('    \t # This is a second comment\n')
        f.seek(0)

        s = SimpleConfig()
        s.readfp(f)
        self.assertEquals([], s.get_sections())

    def test_readfp_defaults(self):
        '''Should allow defaults to be set'''
        f = StringIO.StringIO()
        f.write('[one]\n')
        f.write('a=4\n')
        f.write('[two]\n')
        f.write('b=5\n')
        f.write('[three]\n')
        f.write('[defaults]\n')
        f.write('b=2\n')
        f.seek(0)

        s = SimpleConfig()
        s.defaults.a = 1
        s.defaults.b = 3
        s.readfp(f)

        self.assertEquals(['defaults', 'one', 'three', 'two'],
                          s.get_sections())
        
        self.assertEquals(['a', 'b'], s.defaults.get_settings())
        self.assertEquals(1, s.defaults.a)
        self.assertEquals(2, s.defaults.b)

        self.assertEquals(['a', 'b'], s.one.get_settings())
        self.assertEquals(4, s.one.a)
        self.assertEquals(2, s.one.b)

        self.assertEquals(['a', 'b'], s.two.get_settings())
        self.assertEquals(1, s.two.a)
        self.assertEquals(5, s.two.b)
        
        self.assertEquals(['a', 'b'], s.three.get_settings())
        self.assertEquals(1, s.three.a)
        self.assertEquals(2, s.three.b)

    def test_readfp_defaults_file_only(self):
        '''Should add the defaults section into the config if it doesn't
           exist'''
        f = StringIO.StringIO()
        f.write('[one]\n')
        f.write('[defaults]\n')
        f.write('a=1\n')
        f.seek(0)

        s = SimpleConfig()
        s.readfp(f)

        self.assertEquals(1, s.one.a)

if __name__ == '__main__':
    unittest.main()
