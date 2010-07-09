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
           'SettingError', 'SectionError', 'ConfigError']
import re
import copy

###############################################################################
# Exception classes
###############################################################################
class Error(Exception):
    '''Base exception class'''
    def __init__(self, msg):
        self.msg = msg
        
    def __str__(self):
        return self.msg

class SettingError(Error):
    pass

class SectionError(Error):
    pass

class ConfigError(Error):
    pass

###############################################################################
# SimpleConfig Classes
###############################################################################
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

        # Lists are special since each item gets handled individually
        if isinstance(raw, list):
            new = []
            for v in raw:
                new.append(SimpleConfigSetting.auto_value(v))
            return new
        
        # Only strings can be actually parsed
        if not isinstance(raw, str): return raw
        
        if re.match(r'(?i)(none|null)$', raw): return None
        if re.match(r'-?[0-9]+$', raw): return int(raw)
        if re.match(r'(?i)(true|yes|on)$', raw): return True
        if re.match(r'(?i)(false|no|off)$', raw): return False
        
        # We don't know what it is, so return it as is
        return raw
        
    auto_value = staticmethod(auto_value)

class SimpleConfigSection(object):
    '''Class for holding configuration sections'''

    def __init__(self, settings = {}, auto_value = True, defaults = None):
        self.__dict__['__settings'] = {}

        if defaults:
            self.__dict__['__settings'] = copy.deepcopy(
                    defaults.__dict__['__settings'])

        for s in settings:
            self.set(s, settings[s], auto_value = auto_value)

    def __get_settings(self):
        '''Return the private dictionary of settings'''
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

    def get_settings(self):
        '''Get a list of setting names'''
        settings = self.__get_settings().keys()
        settings.sort()
        return settings

    def __getattr__(self, setting):
        '''Allow accessing settings as attributes of this object'''
        return self.get(setting)

    def __setattr__(self, setting, value):
        '''Allow setting values as attributes of this object'''
        self.set(setting, value)


class SimpleConfig(object):
    '''Simple configuration class'''

    def __init__(self):
        self.__dict__['__sections'] = {}

    def __get_sections(self):
        '''Return the private dictionary of sections'''
        return self.__dict__['__sections']

    def add(self, section):
        '''Add a section to the configuration'''
        sections = self.__get_sections()

        # Just ignore a duplicate section
        if sections.has_key(section): return

        defaults = None
        if sections.has_key('defaults'):
            defaults = sections['defaults']
        
        s = SimpleConfigSection(defaults = defaults)
        sections[section] = s
        return s

    def has(self, section):
        '''Check to see if a section exists'''
        return self.__get_sections().has_key(section)

    def get(self, section):
        '''Return the specified section'''
        sections = self.__get_sections()
        if not sections.has_key(section):
            raise SectionError('invalid section %s' % section)

        return sections[section]

    def delete(self, section):
        '''Delete a section'''
        del self.__get_sections()[section]

    def get_sections(self):
        '''Return a list of sections'''
        sections = self.__get_sections().keys()
        sections.sort()
        return sections

    def __getattr__(self, section):
        '''Allow accessing sections as attributes of this object'''
        if not self.__get_sections().has_key(section):
            self.add(section)
        return self.get(section)

    def readfp(self, fp):
        '''Read the config in from a file'''

        config = SimpleConfig()
        section = None

        i = 0
        for l in fp:
            i += 1
            # Ignore empty line and comments
            if re.match(r'^\s*(#.*)?$', l): continue
            
            # Check for section headers
            r = re.match(r'^\s*\[\s*([^\]]*?)\s*\]\s*$', l)
            if r:
                section = config.add(r.group(1))
                continue
            
            # Check for variables
            r = re.match(r'^\s*([^=]*?)\s*=\s*(.*?)\s*$', l)
            if r:
                if section is None:
                    raise ConfigError('section header missing at line %i: %s' %
                                      (i, l))
                s = r.group(1)
                v = r.group(2)
                section.set(s, v)
                continue
            
            # If we get this far there was a config error
            raise ConfigError('could not parse config file at line %i: %s' %
                    (i, l))
            
        # Write the dict to the object, but first pull out the defaults
        if config.has('defaults'):
            for setting in config.defaults.get_settings():
                self.defaults.set(setting, config.defaults.get(setting))
            config.delete('defaults')

        for section in config.get_sections():
            self.add(section)
            
            for setting in config.get(section).get_settings():
                self.get(section).set(setting, config.get(section).get(setting))

