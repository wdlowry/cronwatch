#!/bin/sh
# $Id$
# vim:ft=sh:sw=4:sta:et
#
# test_collector.sh - cronwatch collector test suite
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


###############################################################################
# Argument/Parameters tests
###############################################################################

# Should fail with an error with any command line arguments
test_fail_noargs () {
    O=`./collector.sh 2>&1 | head -1`
    ./collector.sh > /dev/null 2>&1
    R="$?"

    assertEquals 'ERROR: missing arguments' "$O"
    assertEquals "1" "$R"
}

# -d should set the target directory
test_opt_dir () {
    O=`./collector.sh -z TARGETDIR user host`
    assertEquals '' "$O"

    O=`./collector.sh -z TARGETDIR -d targetdir user host`
    assertEquals 'targetdir' "$O"
}

# -h should display the usage and quit
test_opt_help () {
    O=`./collector.sh -h 2>&1 | head -1`
    ./collector.sh -h > /dev/null 2>&1
    R="$?"
    
    assertEquals 'usage: ./collector.sh [options] username host' "$O"
    assertEquals "0" "$R"
}

# -q should set the queue directory
test_opt_queue () {
    O=`./collector.sh -z QUEUEDIR username host`
    assertEquals '%QUEUEDIR%' "$O"

    O=`./collector.sh -q queuedir -z QUEUEDIR username host`
    assertEquals 'queuedir' "$O"
}

. ../tools/shunit2
