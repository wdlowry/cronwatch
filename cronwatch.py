#!/usr/bin/python
# $Id$
# vim:ft=python:sw=4:sta:et
#
# cronwatch.py - Grab and process output from cron jobs
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

import sys
import os
import signal
import subprocess
import time
import re
import shlex

from optparse import OptionParser
from tempfile import TemporaryFile
from StringIO import StringIO
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from getpass import getuser
from socket import getfqdn, gethostname
from datetime import datetime

from configobj import ConfigObj, flatten_errors, get_extra_values
from validate import Validator, VdtTypeError, VdtValueError, is_list, is_int_list, force_list, ValidateError

###############################################################################
# Global variables
###############################################################################
CONFIGFILE='/etc/cronwatch.conf'

###############################################################################
# Exception class(es)
###############################################################################
class Error(Exception):
    '''Base exception class'''
    def __init__(self, msg):
        self.msg = msg

    def __str__(self):
        return self.msg

###############################################################################
# Helper functions
###############################################################################
def get_user_hostname():
    return '%s@%s' % (getuser(), getfqdn(gethostname()))

def run(args, timeout = -1):
    '''Run an executable
    
       Returns a tuple with a handle to the output and the error code'''

    # Create a temporary file for the output
    output_file = TemporaryFile()

    try:
        process = subprocess.Popen(args, stdout = output_file,
                                   stderr = subprocess.STDOUT,
                                   stdin = open(os.devnull))
        if timeout > -1:
            time.sleep(timeout)
            os.kill(process.pid, signal.SIGTERM)
            return_code = -1

        else:
            return_code = process.wait()

    except Exception, e:
        raise Error('could not run %s: %s' % (args[0], str(e)))

    # I'm not sure if the flush is needed, but better safe than sorry
    output_file.flush()

    # The seek is needed
    output_file.seek(0)

    return (output_file, return_code)

def line_search(line, rx, find_all = False):
    '''Compare a list of regular expressions to a line and return the 
       results'''
    found = []
    for r in rx:
        if r.search(line):
            found.append(r.pattern)

    if found:
        if find_all and len(found) != len(rx):
            return (False, found)
        else:
            return (True, found)
    else:
        return (False, [])

class VdtValueMsgError(VdtValueError):
    def __init__(self, msg):
        ValidateError.__init__(self, msg)

def is_regex(value):
    '''Validator check for regular expressions'''
    if not isinstance(value, basestring):
        raise VdtTypeError(value)

    try: 
        r = re.compile(value)
    except Exception, e:
        raise VdtValueMsgError('invalid regular expression: %s: %s' % 
                               (value, e))

    return r

def is_regex_list(value):
    '''Validator check for list of regular expressions'''
    return [is_regex(r) for r in is_list(value)]

def force_regex_list(value):
    '''Validator check to force a list of regular expressions'''
    return is_regex_list(force_list(value))

def force_int_list(value):
    '''Validator check to force as list of integers'''
    return is_int_list(force_list(value))

def compile_re(regex):
    '''Compile a regex or list of regexes'''

    l = []
    for r in regex:
        try:
            l.append(re.compile(r))
        except TypeError, e:
            raise Error('must be a string or list of strings')

    return l

def read_config(config_file = None):
    '''Read the configuration file'''
    
    # Set up the validation spec
    config_spec = StringIO()
    defaults = '''
        required = force_regex_list(default = list())
        whitelist = force_regex_list(default = None)
        blacklist = force_regex_list(default = list())
        exit_codes = force_int_list(default = list(0))
        email_to = string(default = None)
        email_from = string(default = None)
        email_maxsize = integer(default = 4096, min = -1)
        email_success = boolean(default = False)
        email_sendmail = string(default = /usr/lib/sendmail)
        logfile = string(default = None)
    '''
    config_spec.write('[__many__]\n%s\n[_default_]\n%s' % (defaults, defaults))
    config_spec.seek(0)

    if config_file is None:
        file_error = False
        config_file = CONFIGFILE
    else:
        file_error = True


    # Read the configuration
    try:
        config = ConfigObj(config_file, configspec = config_spec,
                           file_error = file_error)
    except IOError, e:
        raise Error(str(e))
    except Exception, e:
        raise Error('could not read %s: %s' % (config_file, e))

    # Validate the configuration
    extra_checks = { 'force_regex_list': force_regex_list,
                     'force_int_list': force_int_list}
    results = config.validate(Validator(extra_checks), preserve_errors = True)

    if results != True:
        r = flatten_errors(config, results)[0]
        raise Error('configuration error for %s.%s: %s' % 
                    (r[0][0], r[1], r[2]))

    # Check for extra settings
    extra = get_extra_values(config)
    if extra != []:
        raise Error('unknown setting in configuration: %s' % extra[0][1])
    return config

def call_sendmail(args, mail):
    '''Call sendmail and pass in the mail via stdin'''
    
    # Write the mail to a file
    mail_file = TemporaryFile()
    mail_file.write(mail);
    mail_file.flush()
    mail_file.seek(0)

    try:
        process = subprocess.Popen(args, stdout = subprocess.PIPE,
                                   stderr = subprocess.STDOUT,
                                   stdin = mail_file.fileno())
    except Exception, e:
        del mail_file
        raise Error('could not run sendmail: %s: %s' % (args[0], str(e)))
    
    (o, e) = process.communicate()
    r = process.returncode

    if r != 0:
        raise Error('sendmail returned exit code %i: %s' % (r, o))

def send_mail(sendmail, subject, text, to_addr = None, from_addr = None,
              html = None):
    '''Format and send an e-mail'''

    if from_addr is None:
        from_addr = get_user_hostname()

    if to_addr is None:
        to_addr = getuser()

    if html is None:
        msg = MIMEText(text)
    else:
        msg = MIMEMultipart('alternative')

    msg['To'] = to_addr
    msg['From'] = from_addr
    msg['Subject'] = subject

    if not html is None:
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))

    call_sendmail(shlex.split(sendmail) + [to_addr], msg.as_string())

def get_now():
    '''Return a string with the current date and time'''
    return datetime.now().strftime('%c')

###############################################################################
# Watch function
###############################################################################
def watch(args, config = None, tag = None):
    '''Watch a job and capture output'''
    
    # Read the configuration
    config = read_config(config)

    # Run the actual program
    start_time = get_now()
    (oh, exit) = run(args)
    end_time = get_now()

    # Determine the tag automatically
    if tag is None:
        tag = os.path.basename(args[0])
    
    # Determine the conf section to use
    if not config.has_key(tag):
        section = '_default_'
    else:
        section = tag

    errors = []

    # Check for correct error codes
    if exit not in config[section]['exit_codes']:
        errors.append('Exit code (%i) was not a valid exit code' % exit)

    # Create the flags/vars for keeping track of what we've found
    required = {}
    for r in config[section]['required']: required[r.pattern] = False
    
    blacklist = {}
    for r in config[section]['blacklist']: blacklist[r.pattern] = False

    whitelist = True

    outfile = TemporaryFile()

    # Go through the output file and prepare a new one for mailing out
    outline = None
    lines = 0
    for l in oh:
        outline = '  %s' % l
        lines += 1

        # Check for required lines
        found = line_search(l, config[section]['required'])
        if found[0]:
            for p in found[1]:
                required[p] = True

        # Check for whitelist lines
        if config[section]['whitelist'] != None:
            found = line_search(l, config[section]['whitelist'])
            if not found[0]:
                whitelist = False
                outline = '* %s' % l

        # Check for blacklist lines
        found = line_search(l, config[section]['blacklist'])
        if found[0]:
            for p in found[1]:
                blacklist[p] = True
            outline = '! %s' % l

        outfile.write(outline)

    outfile.flush()
    outfile.seek(0)

    #oh.seek(0)

    # Check to make sure all the required regexes got hit
    for r in sorted(required):
        if not required[r]:
            errors.append('Required output missing (%s)' % r)

    # Check to see if anything didn't match the regex whitelist
    if not whitelist:
        errors.append('Output not matched by whitelist ' + 
                      '(denoted by "*" in output)')

    # Check to see if any of the blacklist regexes got hit
    for r in sorted(blacklist):
        if blacklist[r]:
            errors.append('Output matched by blacklist (%s) ' % r +
                          '(denoted by "!" in output)')

    # Bail out if we don't have any errors
    if not errors and not config[section]['email_success']:
        return

    # Construct the e-mail
    subject = 'cronwatch <%s> %s' % (get_user_hostname(), ' '.join(args))
    to_addr = config[section]['email_to']
    from_addr = config[section]['email_from']
    sendmail = config[section]['email_sendmail']

    if errors:
        text = 'The following command line executed with errors:\n'
    else:
        text = 'The following command line executed successfully:\n'

    text += '\t%s\n' % ' '.join(args)
    text += '\n'

    text += 'Started execution at:\t%s\n' % start_time
    text += 'Finished execution at:\t%s\n' % end_time
    text += 'Exit code:\t\t%i\n' % exit
    text += '\n'

    if errors:
        text += 'Errors:\n'
        for e in errors:
            text += '\t* %s\n' % e
        text += '\n\n'

    if outline is None:
        text += 'No output.\n'
    else:
        text += 'Output:\n'
        if config[section]['email_maxsize'] != -1:
            text += outfile.read(config[section]['email_maxsize'] + lines * 2)
            if len(outfile.read(1)) == 0:
               text += '\n[EOF]'
            else:
               text += '\n[Output truncated]'
        else:
            text += outfile.read()
            text += '\n[EOF]'

    send_mail(sendmail, subject, text, to_addr, from_addr)

###############################################################################
# Main function
###############################################################################
def main(argv):
    '''Main function to handle all the command line stuff

       Having this in a separate function makes testing it easier. Note, 
       however, that the command line options won't be tested due to the way
       optparse works. It should be stable anyway.'''
    
    # Handle the command line options
    usage = 'usage: %prog [options] executable'
    parser = OptionParser(usage = usage)
    parser.add_option('-c', '--config', help = 'use CONFIG as the config file')
    parser.add_option('-t', '--tag',
                      help = 'override the default tag with TAG')

    (options, args) = parser.parse_args(args = argv)

    # Should specify at least one command line argument
    if len(args) == 1:
        raise Error('missing command line argument: executable')

    watch(args, config = options.config, tag = options.tag)

###############################################################################
# Python main calling code
###############################################################################
if __name__ == '__main__':
    try:
        main(sys.argv)
    
    except Exception, e:
        sys.stderr.write('ERROR: ' + str(e) + '\n')
        sys.exit(1)

