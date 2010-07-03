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

class Error(Exception):
    '''Base exeception class'''

    def __init__(self, msg = ''):
        Exception.__init__(self, msg)

class NameExistsError(Error):
    '''Raised when a entity by that name has already been defined'''

    def __init__(self, setting):
        Error.__init__(self, 'Already defined: %s' % (setting))

class NameInvalidError(Error):
    '''Raised when a name is invalid'''

    def __init__(self, name):
        Error.__init__(self, 'Does not exist: %s' % (name))

class SettingTypeInvalidError(Error):
    '''Raised when a setting type is invalid'''

    def __init__(self, type):
        Error.__init__(self, 'Setting has invalid type: %s' % (type))

class ConfigSection(object):
    def __init__(self, global_only = False):
        '''Constructor'''
        self.__settings = {}
        self.global_only = global_only

    def add_setting(self, name, type = 'string', default = None):
        '''Add a possible configurable setting'''

        # Check to make sure the setting isn't defined already
        if self.__settings.has_key(name):
            raise NameExistsError(name)

        if type not in ['string', 'int', 'float', 'boolean', 'list']:
            raise SettingTypeInvalidError(type)


        setattr(self, name, property(self.get, self.set))

        self.__settings[name] = {'type': type, 'val': default}

    def get_type(self, name):
        '''Return the type of a setting'''

        # Check to make sure the setting is valid
        if not self.__settings.has_key(name):
            raise NameInvalidError(name)

        return self.__settings[name]['type']

    def get(self, name):
        '''Return the value of a setting'''

        # Check to make sure the setting is valid
        if not self.__settings.has_key(name):
            raise NameInvalidError(name)

        return self.__settings[name]['val']

    def set(self, name, val):
        '''Set a value of a setting'''

        # Check to make sure the setting is valid
        if not self.__settings.has_key(name):
            raise NameInvalidError(name)
        
        self.__settings[name]['val'] = val


    def __getitem__(self, name):
        '''Get a value directly'''
        return self.get(name)

    def __setitem__(self, name, val):
        '''Set a value directly'''
        self.set(name, val)

class Config(object):
    def __init__(self):
        '''Constructor'''
        self.__sections = {}

    def add_section(self, name, global_only = False):
        '''Adds a configuration section'''

        if self.__sections.has_key(name):
            raise NameExistsError(name)

        self.__sections[name] = ConfigSection(global_only)

    def get(self, name):
        '''Returns a section'''

        if not self.__sections.has_key(name):
            raise NameInvalidError(name)

        return self.__sections[name]

    def __getitem__(self, name):
        '''Get a value directly'''
        return self.get(name)


