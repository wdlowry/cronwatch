#!/bin/sh
# $Id$
# vim:ft=sh:sw=4:sta:et
#
# test_wrapper.sh - cronwatch wrapper test suite
#
# Written by David Lowry
# Released under the GPL version 2
#

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

. ../tools/shunit2
