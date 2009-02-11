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
# Helper functions
###############################################################################
# Get the directory that is uploaded
getdir() {
    echo `cat testtmp/scp.out.1 | sed 's#.*:\([^/]*/\)\?\([^_]*_[0-9]*\)_[^_]*$#\2#'`
}

############################################################################### 
# Test environment functions
###############################################################################
oneTimeSetUp() {
    mkdir testbin

    PATH="`pwd`/testbin:$PATH"
    export PATH
    DIR="`pwd`/testtmp/"

    cat > testbin/scp << EOF
#!/bin/sh

# Find out which run this is
if [ ! -r '$DIR/scp.out.1' ] ; then
    i=1
else
    last=\`ls $DIR/scp.out.* | tail -1 | sed 's/[^0-9]*//'\`
    i=\`expr \$last + 1\`
fi

# Capture the command line
echo \$* > "$DIR/scp.out.\$i"

# Flag an error on demand
if [ -r "$DIR/scp.error.\$i" ] ; then
    echo >&2 'scp error!'
    exit 2
fi
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
    O=`./collector.sh 2>&1`

    assertEquals "1" "$?"
    O=`echo "$O" | head -1`
    assertEquals 'ERROR: missing arguments' "$O"
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
    O=`./collector.sh -h 2>&1`
    
    assertEquals "0" "$?"
    O=`echo "$O" | head -1`
    assertEquals 'usage: ./collector.sh [options] username host' "$O"
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
    assertEquals 'ERROR: could not read from queue directory doesntexist' "$O"

}

# -t should test the scp connection
test_opt_test() {
    O=`$C -t -d dir username host 2>&1`
    
    assertEquals '0' "$?"
    assertEquals 'Connection successful!' "$O"

    OUT=`cat testtmp/scp.out.1`
    assertEquals '-B -q -r testtmp/q/test_upload username@host:dir/' "$OUT"
}

# -t should print an error message test the scp connection
test_opt_test_error() {
    touch testtmp/scp.error.1

    O=`$C -t -d dir user host 2>&1`
    
    assertEquals '1' "$?"
    L=`echo "$O" | tail -1`
    assertEquals 'ERROR: could not copy to user@host:dir' "$L"

    L=`echo "$O" | head -1`
    assertEquals 'scp error!' "$L"

    OUT=`cat testtmp/scp.out.1`
    assertEquals '-B -q -r testtmp/q/test_upload user@host:dir/' "$OUT"
}

############################################################################### 
# Copy procedure
###############################################################################
# Should skip locked directories
test_copy_skip_locked() {
    mkdir testtmp/q/1
    touch testtmp/q/1/1
    touch testtmp/q/1.lock
   
    mkdir testtmp/q/2
    touch testtmp/q/2/1
    touch testtmp/q/2.lock
    
    O=`$C user host 2>&1`
    assertEquals '0' "$?"
    assertEquals '' "$O"

    assertFalse '[ -r testtmp/scp.out.1 ]'
}

# Should create a unique directory on the server
test_copy_unique() {
    mkdir testtmp/q/1
    touch testtmp/q/1/1
    touch testtmp/q/1/2

    O=`$C user host 2>&1`
    assertEquals '0' "$?"
    assertEquals '' "$O"

    DIR=`getdir`
    echo "$DIR" | grep "^`hostname`_[0-9][0-9]*$" > /dev/null
    assertEquals '0' "$?"
}

# Should copy a couple simple directory
test_copy_simple() {
    mkdir testtmp/q/1
    touch testtmp/q/1/1
    touch testtmp/q/1/2
    mkdir testtmp/q/2
    touch testtmp/q/2/1
    touch testtmp/q/2/2

    O=`$C user host 2>&1`
    
    assertEquals '0' "$?"
    assertEquals '' "$O"

    DIR=`getdir`

    assertEquals "-B -q -r 1 user@host:${DIR}_1" "`cat testtmp/scp.out.1`"
    assertEquals "-B -q -r 2 user@host:${DIR}_2" "`cat testtmp/scp.out.3`"
}

# Should handle scp errors
test_copy_error() {
    touch testtmp/scp.error.1

    mkdir testtmp/q/1
    touch testtmp/q/1/1
    
    O=`$C -d dir user host 2>&1`
    
    assertEquals '1' "$?"
    L=`echo "$O" | tail -1`
    assertEquals 'ERROR: could not copy to user@host:dir' "$L"
    
    L=`echo "$O" | head -1`
    assertEquals 'scp error!' "$L"
}

# Should copy a transfer complete file
test_copy_complete() {
    mkdir testtmp/q/1
    touch testtmp/q/1/1

    O=`$C user host 2>&1`
    assertEquals '0' "$?"
    assertEquals '' "$O"

    DIR=`getdir`

    assertEquals "-B -q -r 1.complete user@host:${DIR}_1.complete" \
        "`cat testtmp/scp.out.2`"
}

# Should handle scp errors on partial copy
test_copy_complete_error() {
    mkdir testtmp/q/1
    touch testtmp/q/1/1

    touch testtmp/scp.error.2

    O=`$C -d dir user host 2>&1`
    
    assertEquals '1' "$?"
    L=`echo "$O" | tail -1`
    assertEquals 'ERROR: could not copy transfer-complete file to user@host:dir' "$L"

    L=`echo "$O" | head -1`
    assertEquals 'scp error!' "$L"
}

# Should add a directory scp parameters
test_copy_directory() {
    mkdir testtmp/q/1
    touch testtmp/q/1/1

    O=`$C -d dir user host 2>&1`
    assertEquals '0' "$?"
    assertEquals '' "$O"

    DIR=`getdir`

    OUT=`cat testtmp/scp.out.1`
    assertEquals "-B -q -r 1 user@host:dir/${DIR}_1" "$OUT"
    
    OUT=`cat testtmp/scp.out.2`
    assertEquals "-B -q -r 1.complete user@host:dir/${DIR}_1.complete" "$OUT"
}

# Should clean up queued directories
test_copy_cleanup() {
    mkdir testtmp/q/1
    touch testtmp/q/1/1
    mkdir testtmp/q/2
    touch testtmp/q/2/1
    touch testtmp/q/2.lock

    O=`$C user host 2>&1`
    assertEquals '0' "$?"
    assertEquals '' "$O"

    assertTrue '[ ! -d testtmp/q/1 ] '
    assertTrue '[ ! -r testtmp/q/1.complete ] '
}

. ../tools/shunit2
