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
import tempfile

###############################################################################
# SimpleConfig Tests
###############################################################################
class TestSetting(TestBase):
    '''Tests for the Setting class'''

    def test_set_get_name(self):
        '''Should allow the name of the setting to be set and get'''
        s = Setting()
        self.assertEqual(None, s.get_name())
        s.set_name('name')
        self.assertEqual('name', s.get_name())

    def test_set_get(self):
        '''Should allow us to set and get the value'''
        s = Setting()
        self.assertEqual(None, s.get())
        s.set('value')
        self.assertEqual('value', s.get())

    def test_constructor(self):
        '''Should allow the constructor to set the value'''
        s = Setting('value', name = 'name')
        self.assertEqual('value', s.get())
        self.assertEqual('name', s.get_name())

    def test_auto_type(self):
        '''Should return an automatic value'''
        self.assertEqual(None, Setting.auto_type('nOne'))
        self.assertEqual(None, Setting.auto_type('nUll'))
        self.assertEqual(-1, Setting.auto_type('-1'))
        self.assertEqual(0, Setting.auto_type('0'))
        self.assertEqual(1234567890,
                         Setting.auto_type('1234567890'))
        self.assertEqual(True, Setting.auto_type('tRue'))
        self.assertEqual(True, Setting.auto_type('yEs'))
        self.assertEqual(True, Setting.auto_type('oN'))
        self.assertEqual(False, Setting.auto_type('fAlse'))
        self.assertEqual(False, Setting.auto_type('nO'))
        self.assertEqual(False, Setting.auto_type('oFf'))

        # Check to make sure we're checking the whole string
        self.assertEqual('none1', Setting.auto_type('none1'))
        self.assertEqual('1none', Setting.auto_type('1none'))
        self.assertEqual('a-1', Setting.auto_type('a-1'))
        self.assertEqual('-1a', Setting.auto_type('-1a'))
        self.assertEqual('true1', Setting.auto_type('true1'))
        self.assertEqual('1true', Setting.auto_type('1true'))

    def test_auto_type_list(self):
        '''Should work through an list and handle each item'''
        self.assertEqual(['a', 1, None],
                         Setting.auto_type(['a', '1', 'None']))

    def test_set_auto(self):
        '''Should set value automatically and set the raw value as well'''
        s = Setting()
        s.set('1')
        self.assertEquals(1, s.get())
        self.assertEquals('1', s.get(raw = True))
        
        s.set(1)
        self.assertEquals(1, s.get())
        self.assertEquals(1, s.get(raw = True))

    def test_no_auto(self):
        '''Should not set a value automatically'''
        s = Setting()
        s.set('1', raw = True)
        self.assertEquals('1', s.get())

        s = Setting('1', auto_type = False)
        s.set('1')
        self.assertEquals('1', s.get())

class TestSection(TestBase):
    '''Tests for the Section class'''

    def test_set_get_name(self):
        '''Should allow the name of the sectionto be set and get'''
        s = Section()
        self.assertEqual(None, s.get_name())
        s.set_name('name')
        self.assertEqual('name', s.get_name())

    def test_set_get_section(self):
        '''Should allow setting and getting via methods'''
        s = Section()
        s.set_setting('setting', Setting('1'))
        self.assertEquals(1, s.get_setting('setting').get())
        self.assertEquals('setting', s.get_setting('setting').get_name())

    def test_has_setting(self):
        '''Should tell whether a setting exists'''
        s = Section()
        s.set_setting('setting', Setting('1'))
        self.assertTrue(s.has_setting('setting'))

    def test_del_setting(self):
        '''Should delete a setting'''
        s = Section()
        s.set_setting('setting', Setting('1'))
        s.del_setting('setting')
        self.assertFalse(s.has_setting('setting'))

    def test_get_setting_missing(self):
        '''Should raise an exception if the setting does not exist'''
        s = Section()
        self.assertRaisesError(InvalidSettingError,
                               'invalid setting: set',
                               s.get_setting, 'set')

    def test_del_setting_missing(self):
        '''Should raise an exception if the setting does not exist'''
        s = Section()
        self.assertRaisesError(InvalidSettingError,
                               'invalid setting: set',
                               s.del_setting, 'set')

    def test_get_settings(self):
        '''Return a list of settings'''
        s = Section()
        s.set_setting('c', Setting('3'))
        s.set_setting('b', Setting('2'))
        s.set_setting('a', Setting('1'))
        self.assertEquals(['a', 'b', 'c'], s.get_settings())
    
    def test_getattr(self):
        '''Should implement section.setting behavior'''
        s = Section()
        s.set_setting('a', Setting('1'))
        s.set_setting('b', Setting('2'))
        self.assertEquals(1, s.a)
        self.assertEquals(2, s.b)

    def test_setattr(self):
        '''Should implement section.setting = value behavior'''
        s = Section()
        s.a = '1'
        self.assertEquals(1, s.get_setting('a').get())

    def test_delattr(self):
        '''Should implement del section.setting behavior'''
        s = Section()
        s.set_setting('a', Setting('1'))
        del s.a
        self.assertEquals([], s.get_settings())

    def test_iterator(self):
        '''Should allow to work as an iterator'''
        s = Section()
        s.set_setting('b', Setting('2'))
        s.set_setting('c', Setting('3'))
        s.set_setting('a', Setting('1'))

        settings = []
        for i in s:
            settings.append(i)

        self.assertEquals('a', settings[0].get_name())
        self.assertEquals('b', settings[1].get_name())
        self.assertEquals('c', settings[2].get_name())

class TestConfig(TestBase):
    '''Tests for Config class'''

    def test_set_get_setting(self):
        '''Should allow setting and getting via methods'''
        c = Config()
        s1 = Section()
        s2 = Section()
        s1.a = 1
        s2.b = 2

        c.set_section('s1', s1)
        c.set_section('s2', s2)

        self.assertEquals(1, c.get_section('s1').a)
        self.assertEquals(2, c.get_section('s2').b)
        self.assertEquals('s1', c.get_section('s1').get_name())

    def test_has_section(self):
        '''Should check if a section exists'''
        c = Config()
        s = Section()
        self.assertFalse(c.has_section('s'))
        c.set_section('s', s)
        self.assertTrue(c.has_section('s'))

    def test_del_section(self):
        '''Should delete a section'''
        c = Config()
        s = Section()
        c.set_section('s', s)
        c.del_section('s')
        self.assertFalse(c.has_section('s'))

    def test_get_section_missing(self):
        '''Should raise an exception if the section does not exist'''
        c = Config()
        self.assertRaisesError(InvalidSectionError,
                               'invalid section: sec',
                               c.get_section, 'sec')

    def test_del_section_missing(self):
        '''Should raise an exception if the section does not exist'''
        c = Config()
        self.assertRaisesError(InvalidSectionError,
                               'invalid section: sec',
                               c.del_section, 'sec')

    def test_get_sections(self):
        '''Should return a list of sections'''
        c = Config()
        c.set_section('c', Section())
        c.set_section('b', Section())
        c.set_section('a', Section())
        self.assertEquals(['a', 'b', 'c'], c.get_sections())

    def test_get_setting(self):
        '''Should retrieve a setting'''
        c = Config()
        s = Section()
        a = Setting(1)
        c.set_section('s', s)
        s.set_setting('a', a)

        self.assertEqual(1, c.get_setting('s', 'a'))

    def test_get_setting_raw(self):
        '''Should retrieve a setting in the raw format'''
        c = Config()
        s = Section()
        a = Setting('1')
        c.set_section('s', s)
        s.set_setting('a', a)
        
        self.assertEqual('1', c.get_setting('s', 'a', raw = True))

    def test_set_setting(self):
        '''Shold set a setting in a section'''
        c = Config()
        s = Section()
        c.set_section('s', s)
        
        c.set_setting('s', 'a', 1)
        self.assertEqual(1, c.get_setting('s', 'a'))

    def test_set_setting_auto_section(self):
        '''Should automatically create missing sections'''
        c = Config()
        c.set_setting('s', 'a', 1)
        self.assertEqual(1, c.get_setting('s', 'a'))
        self.assertRaises(InvalidSectionError, c.set_setting, 's2', 'a', 1, 
                          auto_section = False)

    def test_set_setting_auto_type(self):
        '''Should have the ability to turn off auto typing'''
        c = Config()
        c.set_setting('s', 'a', '1')
        c.set_setting('s', 'b', '2', auto_type = False)
        self.assertEqual(1, c.get_setting('s', 'a'))
        self.assertEqual('2', c.get_setting('s', 'b'))

    def test_get_attr(self):
        '''Should implement config.section.setting behavior'''
        c = Config()
        c.set_setting('s', 'a', 1)
        self.assertEqual(1, c.s.a)

    def test_get_attr_auto_section(self):
        '''Should implement config.section.setting = value behavior'''
        c = Config()
        c.s.a = 1
        self.assertEqual(1, c.get_setting('s', 'a'))

    def test_del_attr(self):
        '''Should allow sections to be deleted with del'''
        c = Config()
        c.set_section('s', Section())
        del c.s
        self.assertEqual([], c.get_sections())

    def test_iterator(self):
        '''Should allow to work as an iterator'''
        c = Config()
        c.set_section('b', Section())
        c.set_section('c', Section())
        c.set_section('a', Section())
        
        sections = []
        for i in c:
            sections.append(i)

        self.assertEquals('a', sections[0].get_name())
        self.assertEquals('b', sections[1].get_name())
        self.assertEquals('c', sections[2].get_name())

    def test_apply_config(self):
        '''Should apply a different Config object's config to this one'''
        c1 = Config()
        c1.only1.a = 1
        c1.both.only1 = 1
        c1.both.both = 2

        c2 = Config()
        c2.only2.b = 2
        c2.both.only2 = 3
        c2.both.both = [4, 5]

        c1.apply_config(c2)

        self.assertEquals(1, c1.only1.a)
        self.assertEquals(2, c1.only2.b)
        self.assertEquals(1, c1.both.only1)
        self.assertEquals(3, c1.both.only2)
        self.assertEquals([4, 5], c1.both.both)

        # Make sure it was an actual copy
        c1.only2.a = 10
        c1.both.both.append(6)
        self.assertEquals(['b'], c2.only2.get_settings())
        self.assertEquals([4, 5], c2.both.both)
    
    def test_get_set_default_section(self):
        '''Should set and get the name of the default section'''
        c = Config()
        self.assertEqual('defaults', c.get_default_section())
        c.set_default_section('other')
        self.assertEqual('other', c.get_default_section())
        c = Config(default_section = None)
        self.assertEqual(None, c.get_default_section())

    def test_apply_defaults(self):
        '''Should apply default settings to the other sections'''
        c = Config(default_section = None)
        c.mydefaults.a = 1
        c.one.b = 2
        c.two.a = 3

        self.assertEquals(['b'], c.one.get_settings())
        
        c.set_default_section('mydefaults')
        c.apply_defaults()

        self.assertEquals(1, c.one.a)
        self.assertEquals(2, c.one.b)
        self.assertEquals(3, c.two.a)

    def test_apply_defaults_section(self):
        '''Should allow the section to be specified'''
        c = Config(default_section = None)
        c.mydefaults.a = 1
        c.one.b = 2
        c.two.b = 3

        self.assertEquals(['b'], c.one.get_settings())
        self.assertEquals(['b'], c.two.get_settings())
        
        c.set_default_section('mydefaults')
        c.apply_defaults('one')

        self.assertEquals(['a', 'b'], c.one.get_settings())
        self.assertEquals(['b'], c.two.get_settings())

    def test_apply_defaults_set_section(self):
        '''Should apply defaults when a new section is created'''
        c = Config()
        c.defaults.a = 1
        c.defaults.b = 2
        c.one.c = 3

        self.assertTrue(1, c.one.a)
        self.assertTrue(2, c.one.b)


    def test_create_from_file_empty(self):
        '''Should create a mostly empty config'''
        c = Config.create_from_file(StringIO.StringIO())
        self.assertEquals([], c.get_sections())

    def test_create_from_file_comment(self):
        '''Should parse comments and blank lines correctly'''
        f = StringIO.StringIO()
        f.write('  \t \t  \n')
        f.write('# This is a comment\n')
        f.write('    \t # This is a second comment\n')
        f.seek(0)
        
        c = Config.create_from_file(f)
        self.assertEquals([], c.get_sections())

    def test_create_from_file_parse_error(self):
        '''Should raise an exception if something can't be understood'''
        f = StringIO.StringIO()
        f.write('#This is a comment\n')
        f.write('error\n')
        f.seek(0)

        self.assertRaisesError(ConfigParseError,
                'could not parse config file at line 2: error',
                Config.create_from_file, f)

    def test_create_from_file_settings(self):
        '''Should put a couple things in the main section'''
        f = StringIO.StringIO()
        f.write('  \t  a  \t  =  \t  a string  \t  \n')
        f.write('  \t  b b  \t  =  \t  1  \t  \n')
        f.seek(0)
        
        c = Config.create_from_file(f)

        self.assertEquals(['main'], c.get_sections())
        self.assertEquals(['a', 'b b'], c.main.get_settings())
        self.assertEquals('a string', c.main.a)
        self.assertEquals(1, c.get_setting('main', 'b b'))

    def test_create_from_file_section(self):
        '''Should read in the section headers'''
        f = StringIO.StringIO()
        f.write('  \t  [  \t  section  one  \t  ]  \n')
        f.write('a=1\n')
        f.write('[two]')
        f.seek(0)

        c = Config.create_from_file(f)

        self.assertEquals(['section  one', 'two'], c.get_sections())
        self.assertEquals(['a'], c.get_section('section  one').get_settings())
        self.assertEquals(1, c.get_setting('section  one', 'a'))
        self.assertEquals([], c.two.get_settings())

    def test_create_from_file_lists(self):
        '''Should read create arrays if a setting appears more than once'''
        f = StringIO.StringIO()
        f.write('[one]\n')
        f.write('a=1\n')
        f.write('[two]\n')
        f.write('a=1\n')
        f.write('a=2\n')
        f.write('a=3\n')
        f.seek(0)

        c = Config.create_from_file(f)

        self.assertEqual(1, c.one.a)
        self.assertEqual([1, 2, 3], c.two.a)
    
    def test_create_from_file_defaults(self):
        '''Should apply the defaults after creating a file object'''
        f = StringIO.StringIO()
        f.write('[one]\n')
        f.write('[defaults]\n')
        f.write('a=1\n')
        f.seek(0)

        c = Config.create_from_file(f)
        self.assertEquals(1, c.one.a)

    def test_read(self):
        '''Should read config files and apply them to the current file'''
        c = Config()
        c.one.a = 1
        
        f1 = tempfile.NamedTemporaryFile()
        f1.write('[one]\n')
        f1.write('a=2\n')
        f1.write('[two]\n')
        f1.write('b=2')
        f1.seek(0)

        f2 = tempfile.NamedTemporaryFile()
        f2.write('[one]\n')
        f2.write('a=3\n')
        f2.write('[three]\n')
        f2.write('c=3')
        f2.seek(0)

        c.read([f1.name, f2.name])
        
        self.assertEquals(['one', 'three', 'two'], c.get_sections())
        self.assertEquals(['a'], c.one.get_settings())
        self.assertEquals(3, c.one.a)
        self.assertEquals(['b'], c.two.get_settings())
        self.assertEquals(2, c.two.b)
        self.assertEquals(['c'], c.three.get_settings())
        self.assertEquals(3, c.three.c)

    def test_read_single(self):
        '''Should handle a single file'''
        f = tempfile.NamedTemporaryFile()
        f.write('[one]\n')
        f.write('a=1\n')
        f.seek(0)

        c = Config()
        c.read(f.name)

        self.assertEquals(1, c.one.a)

    def test_read_required(self):
        '''Should only fail if the file can't be read if the required flag is
           set'''
        c = Config()
        c.read('nonexistentfile.forsure')
        self.assertRaises(IOError, c.read, 'nonexistentfile.forsure',
                          required = True)

if __name__ == '__main__':
    unittest.main()
