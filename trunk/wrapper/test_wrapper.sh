#!/bin/sh
# $Id$
# vim:ft=sh:sw=4:sta:et
#
# test_wrapper.sh - cronwatch wrapper test suite
#
# Written by David Lowry
# Released under the GPL version 2
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
}

oneTimeTearDown() {
    rm -rf testtmpro
}

setUp() {
    mkdir testtmp
    mkdir -p testtmp/q
}

tearDown() {
    rm -rf testtmp
}

###############################################################################
# Argument/Option tests
###############################################################################

# Should fail with an error without any command line options
test_fail_noargs () {
    O=`./wrapper 2>&1 | head -1`
    ./wrapper > /dev/null 2>&1
    R="$?"

    assertEquals 'ERROR: missing argument' "$O"
    assertEquals "1" "$R"
}

# -c should set the configuration file
test_opt_config () {
    O=`./wrapper -z CONFIGFILE /dev/null`
    assertEquals '' "$O"

    O=`./wrapper -c configfile -z CONFIGFILE /dev/null`
    assertEquals 'configfile' "$O"
}

# -h should display the usage and quit
test_opt_help () {
    O=`./wrapper -h 2>&1 | head -1`
    ./wrapper -h > /dev/null 2>&1
    R="$?"
    
    assertEquals 'usage: ./wrapper [options] executable [arguments]' "$O"
    assertEquals "0" "$R"
}

# -q should set the queue directory
test_opt_queue () {
    O=`./wrapper -z QUEUEDIR /dev/null`
    assertEquals '/var/lib/cronwatch/wrapper' "$O"

    O=`./wrapper -q queuedir -z QUEUEDIR /dev/null`
    assertEquals 'queuedir' "$O"
}

# -u should set the unique id
test_opt_uid () {
    O=`./wrapper -z UNIQUEID /dev/null`
    assertEquals '' "$O"

    O=`./wrapper -u uniqueid -z UNIQUEID /dev/null`
    assertEquals 'uniqueid' "$O"
}

# Should flag an error if the config file doesn't exist or isn't readable
test_configfile_readable () {
    O=`./wrapper -c doesntexist /dev/null 2>&1`
    R="$?"

    assertEquals 'ERROR: could not read config file doesntexist' "$O"
    assertEquals "1" "$R"
    
    test "$ROOTRUN" = '1' && return

    assertTrue 'testtmpro/unreadable does not exist' \
        '[ -e testtmpro/unreadable ]'
    
    O=`./wrapper -c testtmpro/unreadable /dev/null 2>&1`
    R="$?"

    assertEquals 'ERROR: could not read config file testtmpro/unreadable' "$O"
    assertEquals "1" "$R"
}

# TODO add test to check to make sure config file gets copied

test_queuedir_writeable () {
    O=`./wrapper -q doesntexist /dev/null 2>&1`
    R="$?"
    
    assertEquals 'ERROR: could not write to queue directory doesntexist' "$O"
    assertEquals "1" "$R"

    test "$ROOTRUN" = '1' && return

    assertTrue 'testtmpro/unwriteable does not exist' \
        '[ -e testtmpro/unwriteable ]'
    
    O=`./wrapper -q testtmpro/unwriteable /dev/null 2>&1`
    R="$?"

    assertEquals 'ERROR: could not write to queue directory testtmpro/unwriteable' "$O"
    assertEquals "1" "$R"
}

###############################################################################
# Actual run
###############################################################################
# Should create a lock file
test_lockfile () {

}

. ../tools/shunit2
