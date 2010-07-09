#!/usr/bin/python
# $Id$
# vim:ft=python:sw=4:sta:et
#
# simpleconfig - Simple configuration class
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

__all__ = ['SimpleConfig', 'SimpleConfigSection', 'SimpleConfigSetting',
           'SimpleConfigError', 'SettingError']
import re

###############################################################################
# Exception classes
###############################################################################
class SimpleConfigError(Exception):
    '''Base exception class'''
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg

class SettingError(SimpleConfigError):
    pass

class SimpleConfig(object):
    '''Simple configuration class'''

class SimpleConfigSection(object):
    '''Class for holding configuration sections'''

    def __init__(self, settings = {}, auto_value = True):
        self.__dict__['__settings'] = {}

        for s in settings:
            self.set(s, settings[s], auto_value = auto_value)

    def __get_settings(self):
        '''Return the dictionary of settings'''
        return self.__dict__['__settings']

    def set(self, setting, value, auto_value = True):
        '''Set the value for a setting'''
        self.__get_settings()[setting] = SimpleConfigSetting(value,
                                                       auto_value = auto_value)

    def get(self, setting, raw = False):
        '''Gets a value for the setting'''
        if not self.__get_settings().has_key(setting):
            raise SettingError('invalid setting %s' % setting)

        return self.__get_settings()[setting].get(raw = raw)

    def __getattr__(self, setting):
        '''Allow accessing settings as attributes of this object'''
        return self.get(setting)

    def __setattr__(self, setting, value):
        '''Allow setting values as attributes of this object'''
        self.set(setting, value)


class SimpleConfigSetting(object):
    '''Class for holding the configuration settings for a section'''
    def __init__(self, value = None, auto_value = True):
        self.set(value, auto_value)

    def set(self, value, auto_value = True):
        '''Set the value'''
        if auto_value:
            self.__value = SimpleConfigSetting.auto_value(value)
        else:
            self.__value = value

        self.__raw = value

    def get(self, raw = False):
        '''Get the value'''
        if raw:
            return self.__raw

        return self.__value

    def auto_value(raw):
        '''Determine the type of a value and translate it into a Python type'''

        if not isinstance(raw, str): return raw
        
        if re.match(r'(?i)(none|null)$', raw): return None
        if re.match(r'-?[0-9]+$', raw): return int(raw)
        if re.match(r'(?i)(true|yes|on)$', raw): return True
        if re.match(r'(?i)(false|no|off)$', raw): return False

        return raw
        
    auto_value = staticmethod(auto_value)
        
