#!/bin/sh
# $Id$
# vim:ft=sh:sw=4:sta:et
#
# test_script.sh - Simple shell program to generate test output
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

# Based on the first argument, print out some test output or do a test action
usage() {
    echo "usage: $0 TESTCASE [OUT] [ARGS]"
    exit 1
}

if [ -z "$1" ] ; then
    usage
fi

CMD="$1"
shift 

if [ -n "$1" ] ; then
    OUT="$1"
    shift
fi

case "$CMD" in
    simple)
        echo stdout
        echo stderr 1>&2
        echo stdout again
        exit 10
        ;;
    read)
        read INPUT
        echo "$INPUT"
        exit 0
        ;;
    timeout)
        sleep 1
        echo 'timeout'
        exit 0
        ;;
    sendmail)
        cat > "$OUT"
        exit 0
        ;;
    quiet)
        echo "quiet $*" > "$OUT"
        exit 0
        ;;
    exit)
        exit $1
        ;;
    out)
        while [ -n "$1" ] ; do
            echo $1
            shift
        done
        ;;
    *)
        usage
        ;;
esac

