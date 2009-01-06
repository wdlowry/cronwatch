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
    O=`./wrapper.sh 2>&1 | head -1`
    ./wrapper.sh > /dev/null 2>&1
    R="$?"

    assertEquals 'ERROR: missing argument' "$O"
    assertEquals "1" "$R"
}

. ../tools/shunit2
