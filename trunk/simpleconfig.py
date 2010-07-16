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

__all__ = ['Setting', 'Section', 'Config',
           'InvalidSettingError', 'InvalidSectionError', 'ConfigParseError']
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

class InvalidSettingError(Error):
    '''The specified setting is missing'''

class InvalidSectionError(Error):
    '''The specified section is missing'''

class ConfigParseError(Error):
    '''There was a parse error while reading the configuration file'''

###############################################################################
# simpleconfig Classes
###############################################################################
class Setting(object):
    '''Class for holding invidual configuration settings'''
    def __init__(self, value = None, auto_type = True, name = None):
        self.auto_type = auto_type
        self.set_name(name)
        self.set(value)

    def get_name(self):
        '''Return the name of the setting'''
        return self.__name

    def set_name(self, name):
        '''Set the name of the setting'''
        self.__name = name

    def set(self, value, raw = False):
        '''Set the value'''
        if self.auto_type and not raw:
            self.__value = Setting.auto_type(value)
        else:
            self.__value = value

        self.__raw = value

    def get(self, raw = False):
        '''Get the value'''
        if raw:
            return self.__raw

        return self.__value

    def auto_type(raw):
        '''Determine the type of a value and translate it into a Python type'''

        # Lists are special since each item gets handled individually
        if isinstance(raw, list):
            new = []
            for v in raw:
                new.append(Setting.auto_type(v))
            return new
        
        # Only strings can be actually parsed
        if not isinstance(raw, str): return raw
        
        if re.match(r'(?i)(none|null)$', raw): return None
        if re.match(r'-?[0-9]+$', raw): return int(raw)
        if re.match(r'(?i)(true|yes|on)$', raw): return True
        if re.match(r'(?i)(false|no|off)$', raw): return False

        r = re.match(r'''('|")(.*)\1$''', raw)
        if r: return r.group(2)
        
        # We don't know what it is, so return it as is
        return raw
        
    auto_type = staticmethod(auto_type)

class Section(object):
    '''Class for holding configuration sections'''

    def __init__(self):
        self.__dict__['__settings'] = {}
        self.set_name(None)

    def get_name(self):
        '''Get the name'''
        return self.__dict__['__name']

    def set_name(self, name):
        '''Set the name'''
        self.__dict__['__name'] = name

    def set_setting(self, setting, value):
        '''Set the value for a setting'''
        assert isinstance(setting, str)
        assert isinstance(value, Setting)
        value.set_name(setting)
        self.__dict__['__settings'][setting] = value

    def get_setting(self, setting):
        '''Gets a value for the setting'''
        if setting == '__deepcopy__': return None
        if not self.has_setting(setting):
            raise InvalidSettingError('invalid setting: %s' % setting)
        return self.__dict__['__settings'][setting]

    def has_setting(self, setting):
        '''Checks whether a setting exists'''
        return self.__dict__['__settings'].has_key(setting)

    def del_setting(self, setting):
        '''Deletes a setting'''
        if not self.has_setting(setting):
            raise InvalidSettingError('invalid setting: %s' % setting)
        del self.__dict__['__settings'][setting]

    def get_settings(self):
        '''Get a list of setting names'''
        settings = self.__dict__['__settings'].keys()
        settings.sort()
        return settings

    def __getattr__(self, setting):
        '''Allow accessing settings as attributes of this object'''
        return self.get_setting(setting).get()

    def __setattr__(self, setting, value):
        '''Allow setting values as attributes of this object'''
        self.set_setting(setting, Setting(value))

    def __delattr__(self, setting):
        '''Allow settings to be deleted as attributes'''
        self.del_setting(setting)

    def __iter__(self):
        '''Allow settings to be pulled using an iterator'''
        class iter(object):
            def __init__(my_self):
                settings = self.get_settings()
                # Generate a list of settings
                my_self.settings = []
                for s in settings:
                    my_self.settings.append(self.get_setting(s))
            def next(self):
                if len(self.settings) > 0:
                    return self.settings.pop(0)
                else:
                    raise StopIteration()
        return iter()

class Config(object):
    '''Simple configuration class'''
    def __init__(self, default_section = 'defaults'):
        self.__dict__['__sections'] = {}
        self.__dict__['__default'] = default_section

    def set_section(self, name, section):
        '''Add a section to the config'''
        assert isinstance(name, str)
        assert isinstance(section, Section)
        section.set_name(name)
        self.__dict__['__sections'][name] = section
        self.apply_defaults()

    def get_section(self, section):
        '''Get a section from the config'''
        if not self.has_section(section):
            raise InvalidSectionError('invalid section: %s' % section)
        return self.__dict__['__sections'][section]

    def has_section(self, section):
        '''Check if a section exists'''
        return self.__dict__['__sections'].has_key(section)

    def del_section(self, section):
        '''Should delete a section'''
        if not self.has_section(section):
            raise InvalidSectionError('invalid section: %s' % section)
        del self.__dict__['__sections'][section]

    def get_sections(self):
        '''Return a list of sections'''
        sections = self.__dict__['__sections'].keys()
        sections.sort()
        return sections

    def get_setting(self, section, setting, raw = False):
        '''Should return a setting in a section'''
        return self.get_section(section).get_setting(setting).get(raw)

    def set_setting(self, section, setting, value, auto_section = True,
                    auto_type = True):
        '''Should set a setting in a section'''
        if not self.has_section(section) and auto_section:
            self.set_section(section, Section())
        self.get_section(section).set_setting(setting,
                Setting(value, auto_type = auto_type))

    def __getattr__(self, section):
        '''Allow accessing settings as attributes of this object'''
        if not self.has_section(section):
            self.set_section(section, Section())
        return self.get_section(section)

    def __delattr__(self, section):
        '''Allow sections to be deleted as attributes'''
        self.del_section(section)

    def __iter__(self):
        '''Allow sections to be pulled using an iterator'''
        class iter(object):
            def __init__(my_self):
                sections = self.get_sections()
                # Generate a list of sections
                my_self.sections = []
                for s in sections:
                    my_self.sections.append(self.get_section(s))
            def next(self):
                if len(self.sections) > 0:
                    return self.sections.pop(0)
                else:
                    raise StopIteration()
        return iter()
    
    def apply_config(self, other):
        '''Apply another configurations config'''
        assert isinstance(other, Config)
        
        for section in other:
            sec_name = section.get_name()
            if not self.has_section(sec_name):
                self.set_section(sec_name, copy.deepcopy(section))
            else:
                for setting in section:
                    set_name = setting.get_name()
                    self.get_section(sec_name).set_setting(set_name,
                            copy.deepcopy(setting))

    def set_default_section(self, section):
        '''Set the section that has the defaults'''
        self.__dict__['__default'] = section

    def get_default_section(self):
        '''Get the default section'''
        return self.__dict__['__default']

    def apply_defaults(self, section = None):
        '''Apply the default section to the other sections'''
        default = self.__dict__['__default']
        
        if not self.has_section(default):
            return

        if section is None:
            sections = self.__dict__['__sections'].values()
        else:
            sections = [self.get_section(section)]

        for section in sections:
            # Skip the default section of course
            if section.get_name() == default: continue

            for setting in self.get_section(default):
                if not section.has_setting(setting.get_name()):
                    section.set_setting(setting.get_name(),
                                        copy.deepcopy(setting))
    
    def create_from_file(fp):
        '''Create a config file from a file object'''
        config = Config()
        section = 'main'
    
        ln = 0
        for line in fp:
            ln += 1
            
            # Ignore empty line and comments
            if re.match(r'^\s*(#.*)?$', line): continue

            # Check for section headers
            r = re.match(r'^\s*\[\s*([^\]]*?)\s*\]\s*$', line)
            if r:
                section = r.group(1)

                # Add empty sections
                if not config.has_section(section):
                    config.set_section(section, Section())
                continue

            # Parse settings
            r = re.match(r'^\s*([^=]*?)\s*=\s*(.*?)\s*$', line)
            if r:
                setting = r.group(1)
                value = r.group(2)
                
                # If the setting already exists, append to the array
                if (config.has_section(section)
                    and config.get_section(section).has_setting(setting)):

                    # Make it an array if it isn't already
                    if not isinstance(config.get_setting(section, setting),
                                      list):
                        config.get_section(section).get_setting(setting).set(
                                [config.get_setting(section, setting)])
                    new_list = config.get_setting(section,setting)
                    new_list.append(value)
                    config.get_section(section
                                      ).get_setting(setting).set(new_list)
                else:
                    config.set_setting(section, r.group(1), r.group(2))
                continue

            # If we get this far there was a config error
            raise ConfigParseError('could not parse config file at line %i: %s'
                                   % (ln, line))
            
        config.apply_defaults()
        return config


    create_from_file = staticmethod(create_from_file)

    def read(self, files, required = False):
        '''Read in config files and apply them to this object'''

        if not isinstance(files, list):
            files = [files]

        for fn in files:
            if required:
                fp = open(fn)
            else:
                try:
                    fp = open(fn)
                except IOError, e:
                    return
                
            c = Config.create_from_file(fp)
            self.apply_config(c)

