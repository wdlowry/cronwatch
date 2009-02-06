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
# Test environment functions
###############################################################################
oneTimeSetUp() {
    mkdir testbin

    export PATH=./testbin:$PATH

    cat > testbin/scp << EOF
#!/bin/sh
echo \$* > testtmp/scp.out
grep error testtmp/scp.out > /dev/null 2>&1
if [ ! "\$?" = '1' ] ; then echo >&2 error!;  fi
exit 2
EOF

    chmod +x testbin/scp

    C='./collector.sh -q testtmp/q'
}

oneTimeTearDown() {
    rm -rf testbin
}

setUp() {
    mkdir testtmp
    mkdir testtmp/q
}

tearDown() {
    rm -rf testtmp
}

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

# Make sure the queue dir is readable
test_queuedir_readable () {
    O=`./collector.sh -q doesntexist username host 2>&1`
    assertEquals '1' "$?"
    assertEquals 'ERROR: could not read queue directory doesntexist' "$O"

}

# -t should test the scp connection
test_opt_test() {
    O=`$C -t -d somedir username host 2>&1`
    R="$?"
    assertEquals 'Connection successful!' "$O"
    assertEquals '0' "$R"

    OUT=`cat testtmp/scp.out`
    assertEquals '-B -q -r testtmp/q/test_upload username@host:somedir' "$OUT"
}

# -t should print an error message test the scp connection
test_opt_test_error() {
    O=`$C -t -d somedir user errorhost 2>&1`
    R="$?"
    assertEquals 'error: could not upload to user@errorhost:somedir' "$O"
    assertEquals '1' "$R"

    OUT=`cat testtmp/scp.out`
    assertEquals '-B -q -r testtmp/q/test_upload user@errorhost:somedir' "$OUT"
}


. ../tools/shunit2
