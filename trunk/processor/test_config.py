#!/usr/bin/python
# $Id$
# vim:ft=python:sw=4:sta:et
#
# config.py - Configuration classes and stuff for cronwatch
# Copyright (C) 2009 David Lowry < wdlowry _remove_ at _remove_ gmail dot com >
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
#

import unittest

execfile('config.py')

class TestConfigSection(unittest.TestCase):

    def setUp(self):
        self.c = ConfigSection()
        self.c.add_setting('s')
        self.c.add_setting('i', 'int', 2)
        self.c.add_setting('f', 'float', 2.1)
        self.c.add_setting('b', 'boolean', True)
        self.c.add_setting('l', 'list', ['a', 'b'])

    def tearDown(self):
        pass

    def test_add_setting_already_exists(self):
        '''Should throw an exception if the setting already exists'''
        self.assertRaises(NameExistsError, self.c.add_setting, 's')

    def test_add_setting_invalid_type(self):
        '''Should throw an exception if the setting type is invalid'''
        self.assertRaises(SettingTypeInvalidError, self.c.add_setting, 'new',
                          'type')

    def test_get_type_invalid_name(self):
        '''Should throw an exception if the name is invalid'''
        self.assertRaises(NameInvalidError, self.c.get_type, 'm')

    def test_get_type(self):
        '''Should return the type of the different name'''
        self.assertEqual(self.c.get_type('s'), 'string')
        self.assertEqual(self.c.get_type('i'), 'int')
        self.assertEqual(self.c.get_type('f'), 'float')
        self.assertEqual(self.c.get_type('b'), 'boolean')
        self.assertEqual(self.c.get_type('l'), 'list')

    def test_get_type_invalid_name(self):
        '''Should throw an exception if the name is invalid'''
        self.assertRaises(NameInvalidError, self.c.get, 'm')

    def test_get(self):
        '''Should return the value of the setting'''
        self.assertEqual(self.c.get('s'), None)
        self.assertEqual(self.c.get('i'), 2)
        self.assertEqual(self.c.get('f'), 2.1)
        self.assertEqual(self.c.get('b'), True)
        self.assertEqual(self.c.get('l'), ['a', 'b'])

    def test_set_type_invalid_name(self):
        '''Should throw an exception if the name is invalid'''
        self.assertRaises(NameInvalidError, self.c.set, 'm', 1)

    def test_set_type(self):
        '''Should set the value of a setting'''
        self.c.set('s', 'a')
        self.assertEqual(self.c.get('s'), 'a')

    def test_getitem(self):
        '''Should be able to get the attribute directly'''
        self.assertEqual(self.c['i'], 2)

    def test_setattr(self):
        '''Should be able to set the attribute directly'''
        self.c['i'] = 3
        self.assertEqual(self.c.get('i'), 3)

    def test_global_only(self):
        '''Should be able to specify the global_only property'''
        self.assertEqual(self.c.global_only, False)
        c = ConfigSection(global_only = True)
        self.assertEqual(c.global_only, True)

class TestConfig(unittest.TestCase):
    def setUp(self):
        self.c = Config()
        
        self.c.add_section('g', True)
        self.c.add_section('l')

    def test_add_section_already_exists(self):
        '''Should throw an exception if the section already exists'''
        self.assertRaises(NameExistsError, self.c.add_section, 'g')

    def test_get_invalid_name(self):
        '''Should throw an exception if the name is invalid'''
        self.assertRaises(NameInvalidError, self.c.get, 'm')

    def test_get(self):
        '''Should return a section'''
        self.assert_(isinstance(self.c.get('g'), ConfigSection))

    def test_getitem(self):
        '''Should return a section'''
        self.assert_(isinstance(self.c['g'], ConfigSection))

    def test_different_sections(self):
        '''Tests to make sure sections are working correctly'''
        self.c['g'].add_setting('i1', 'int', 1)
        self.c['l'].add_setting('i2', 'int', 2)
        self.assertEquals(self.c['g']['i1'], 1)
        self.assertEquals(self.c['l']['i2'], 2)



if __name__ == '__main__':
    unittest.main()
