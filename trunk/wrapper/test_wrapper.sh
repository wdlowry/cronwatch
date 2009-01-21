#!/bin/sh
# $Id$
# vim:ft=sh:sw=4:sta:et
#
# test_wrapper.sh - cronwatch wrapper test suite
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

# Check to make sure we're not running as root
touch tmpfile
chmod 000 tmpfile

if [ -r tmpfile ] ; then
    cat << EOF
WARNING! WARNING! WARNING! WARNING! WARNING! WARNING! WARNING! WARNING!

It appears that you're running as root. Some of the tests will be skipped
because they will not work correctly.

WARNING! WARNING! WARNING! WARNING! WARNING! WARNING! WARNING! WARNING!

EOF
    ROOTRUN='1'
fi

rm -f tmpfile

###############################################################################
# Helper functions
###############################################################################
# Get the queue directory
getqd() {
    find testtmp/q -type d | grep -v '^testtmp/q$'
}


###############################################################################
# Test environment functions
###############################################################################
# These are files that don't need to be created/destroyed for each test
oneTimeSetUp() {
    mkdir testtmpro
    
    # Create an "unreadable" file (this won't work correctly for root)
    touch testtmpro/unreadable
    chmod 000 testtmpro/unreadable

    # Create an "unwriteable" file (this won't work correctly for root)
    mkdir testtmpro/unwriteable
    chmod 555 testtmpro/unwriteable

    # Create an "unrunable" file (this will actually work for root)
    touch testtmpro/unrunable
    chmod 644 testtmpro/unrunable

    # Create a simple executable
    cat > testtmpro/simple << EOF
#!/bin/sh
if [ -n "\$1" ] ; then sleep \$1; fi
echo >&2 stderr
echo stdout
exit 2
EOF
    chmod +x testtmpro/simple

    # Create a executable that processes arguments
    cat > testtmpro/args << EOF
#!/bin/sh
for ARG in "\$@"; do
    echo \$ARG
done
EOF
    chmod +x testtmpro/args
    
    # Create a executable that processes arguments
    cat > testtmpro/env << EOF
#!/bin/sh
echo \$VAR
EOF
    chmod +x testtmpro/env
    
    # Create a config file
    echo 'config' > testtmpro/config
}

oneTimeTearDown() {
    rm -rf testtmpro
}

setUp() {
    mkdir testtmp
    mkdir -p testtmp/q

    W='./wrapper.sh -q testtmp/q'
}

tearDown() {
    rm -rf testtmp
}

###############################################################################
# Argument/Option tests
###############################################################################

# Should fail with an error without any command line options
test_fail_noargs () {
    O=`./wrapper.sh 2>&1 | head -1`
    ./wrapper.sh > /dev/null 2>&1
    R="$?"

    assertEquals 'ERROR: missing argument' "$O"
    assertEquals "1" "$R"
}

# -c should set the configuration file
test_opt_config () {
    O=`./wrapper.sh -z CONFIGFILE /dev/null`
    assertEquals '' "$O"

    O=`./wrapper.sh -c configfile -z CONFIGFILE /dev/null`
    assertEquals 'configfile' "$O"
}

# -h should display the usage and quit
test_opt_help () {
    O=`./wrapper.sh -h 2>&1 | head -1`
    ./wrapper.sh -h > /dev/null 2>&1
    R="$?"
    
    assertEquals 'usage: ./wrapper.sh [options] executable [arguments]' "$O"
    assertEquals "0" "$R"
}

# -q should set the queue directory
test_opt_queue () {
    O=`./wrapper.sh -z QUEUEDIR /dev/null`
    assertEquals '%QUEUEDIR%' "$O"

    O=`./wrapper.sh -q queuedir -z QUEUEDIR /dev/null`
    assertEquals 'queuedir' "$O"
}

# -u should set the unique id
test_opt_uid () {
    O=`./wrapper.sh -z UNIQUEID /dev/null`
    assertEquals '' "$O"

    O=`./wrapper.sh -u uniqueid -z UNIQUEID /dev/null`
    assertEquals 'uniqueid' "$O"
}

# Should flag an error if the config file doesn't exist or isn't readable
test_configfile_readable () {
    O=`./wrapper.sh -c doesntexist /dev/null 2>&1`
    R="$?"

    assertEquals 'ERROR: could not read config file doesntexist' "$O"
    assertEquals "1" "$R"
    
    test "$ROOTRUN" = '1' && return

    assertTrue 'testtmpro/unreadable does not exist' \
        '[ -f testtmpro/unreadable ]'
    
    O=`./wrapper.sh -c testtmpro/unreadable /dev/null 2>&1`
    R="$?"

    assertEquals 'ERROR: could not read config file testtmpro/unreadable' "$O"
    assertEquals "1" "$R"
}

# TODO add test to check to make sure config file gets copied

test_queuedir_writeable () {
    O=`./wrapper.sh -q doesntexist /dev/null 2>&1`
    R="$?"
    
    assertEquals 'ERROR: could not write to queue directory doesntexist' "$O"
    assertEquals "1" "$R"

    test "$ROOTRUN" = '1' && return

    assertTrue 'testtmpro/unwriteable does not exist' \
        '[ -d testtmpro/unwriteable ]'
    
    O=`./wrapper.sh -q testtmpro/unwriteable /dev/null 2>&1`
    R="$?"

    assertEquals 'ERROR: could not write to queue directory testtmpro/unwriteable' "$O"
    assertEquals "1" "$R"
}

test_missing_executable () {
    O=`$W doesntexist 2>&1`
    R="$?"

    assertEquals "ERROR: could not run doesntexist" "$O"
    assertEquals "1" "$R"
    
    assertTrue 'testtmpro/unrunable does not exist' \
        '[ -f testtmpro/unrunable ]'

    O=`$W testtmpro/unrunable 2>&1`
    R="$?"

    assertEquals "ERROR: could not run testtmpro/unrunable" "$O"
    assertEquals "1" "$R"
}


###############################################################################
# Actual run
###############################################################################
# Should create and remove the lock file
test_lock_create () {
    O=`$W -z KEEPLOCK testtmpro/simple 2>&1`
    R="$?"

    assertEquals "" "$O"
    assertEquals "0" "$R"

    QD=`getqd`
    assertTrue 'cat $QD.lock | egrep "^[0-9][0-9][0-9]*$"'
}

# Should clean up the lock file on exit
test_lock_cleanup () {
    O=`$W testtmpro/simple 2>&1`
    R="$?"

    assertEquals "" "$O"
    assertEquals "0" "$R"

    QD=`getqd`
    assertTrue "[ ! -f $QD.lock ]"
}


# Should create a queue directory in the correct format
test_queuedir () {
    O=`$W testtmpro/simple 2>&1`
    R="$?"

    assertEquals "" "$O"
    assertEquals "0" "$R"

    QD=`getqd`
    QD=`basename "$QD"`

    REGEX="^[0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9][0-9]"
    REGEX="$REGEX[0-9][0-9]_[0-9][0-9]+$"

    assertTrue "echo $QD | egrep '$REGEX'"
}

# Should capture all output from run
test_output () {
    O=`$W testtmpro/simple 2>&1`
    R="$?"
    
    assertEquals "" "$O"
    assertEquals "0" "$R"

    QD=`getqd`

    # Note: this has to be split over two line to match the linebreaks
    assertEquals 'stderr
stdout' "`cat $QD/output`"
}

# Should handle arguments correctly
test_call_args () {
    O=`$W testtmpro/args first second 'third fourth' 2>&1`
    R="$?"
    
    assertEquals "" "$O"
    assertEquals "0" "$R"

    QD=`getqd`

    # Note: this has to be split over two line to match the linebreaks
    assertEquals 'first
second
third fourth' "`cat $QD/output`"
}

# Should have a clean environment
test_env () {
    VAR=1
    export VAR
    O=`$W testtmpro/env 2>&1`
    R="$?"

    assertEquals "" "$O"
    assertEquals "0" "$R"

    QD=`getqd`

    assertEquals '' "`cat $QD/output`"

}

# Should copy config file
test_configfile () {
    O=`$W -c testtmpro/config testtmpro/simple 2>&1`
    R="$?"
    
    assertEquals "" "$O"
    assertEquals "0" "$R"

    QD=`getqd`

    assertEquals 'config' "`cat $QD/config`"
}

# Should capture the status to the status file
test_status () {
    O=`$W -u 'unique id' testtmpro/simple 2 arg1 arg2 2>&1`
    R="$?"
    
    assertEquals "" "$O"
    assertEquals "0" "$R"

    QD=`getqd`
    ST="$QD/status"

    START=`grep START $ST | cut -f 2- -d =`
    STOP=`grep STOP $ST | cut -f 2- -d =`
    RETCODE=`grep RETCODE $ST | cut -f 2- -d =`
    FULLPATH=`grep FULLPATH $ST | cut -f 2- -d =`
    UNIQUEID=`grep UNIQUEID $ST | cut -f 2- -d =`
    ARGUMENTS=`grep ARGUMENTS $ST | cut -f 2- -d =`

    REGEX="^[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]"
    REGEX="$REGEX [0-9][0-9]:[0-9][0-9]:[0-9][0-9]Z$"

    assertTrue "echo $START | egrep '$REGEX'"
    assertTrue "echo $STOP | egrep '$REGEX'"
    assertNotEquals "$START" "$STOP"
    assertEquals '2' "$RETCODE"
    assertEquals 'testtmpro/simple' "$FULLPATH"
    assertEquals 'unique id' "$UNIQUEID"
    assertEquals '2 arg1 arg2' "$ARGUMENTS"

}

. ../tools/shunit2
