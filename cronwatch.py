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
from optparse import OptionParser
import subprocess
import tempfile
import time
import re
import simpleconfig

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
def run(args, timeout = -1):
    '''Run an executable
    
       Returns a tuple with a handle to the output and the error code'''

    # Create a temporary file for the output
    output_file = tempfile.TemporaryFile()

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

def filter_text(rx, fh):
    '''Search file object fh for the rx(es) in rx'''

    # Convert to a list if it isn't one
    if not isinstance(rx, list):
        rx = [rx]

    # Create a working dict with the hashes
    rxes = {}
    results = {}
    for r in rx:
        try:
            rxes[r] = re.compile(r)
        except Exception, e:
            raise Error('invalid regex "%s": %s' % (r, str(e)))

        results[r] = []

    # Cycle through the lines and try each regex against it
    i = 0 
    for line in fh:
        for r in rxes:
            if rxes[r].search(line) != None:
                results[r].append(i)
        i += 1

    return results
        
def read_config(config_file = None):
    '''Read the configuration file'''
    config = simpleconfig.Config()

    config.defaults.required = None
    config.defaults.whitelist = None
    config.defaults.blacklist = '.*'
    config.defaults.exit_codes = 0
    config.defaults.email = 'root'
    config.defaults.email_maxsize = 4096
    config.defaults.email_success = False
    config.defaults.email_sendmail = '/usr/lib/sendmail'
    config.defaults.logfile = None

    if not config_file is None:
        config.read(config_file, required = True)
    else:
        config.read(CONFIGFILE)

    for sec in config:
        for s in sec:
            if s.get_name() not in ['required', 'whitelist', 'blacklist',
                                    'exit_codes', 'email', 'email_maxsize',
                                    'email_success', 'email_sendmail',
                                    'logfile']:
                raise Error('unknown option %s in section %s' %
                            (s.get_name(), sec.get_name()))

    return config

###############################################################################
# Watch function
###############################################################################
def watch(args, config = None, tag = None):
    '''Watch a job and capture output'''

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

