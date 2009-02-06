#!/bin/sh
# $Id$
# vim:ft=sh:sw=4:sta:et
#
# collector - Move cron jobs status and output to central server
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

# Print out the usage
usage () {
    cat << EOF
usage: $0 [options] username host

options:
  -d                    target directory
  -q                    queue directory
  -t                    test the ssh/scp connection
EOF
}

# Print an error message and exit
error () {
    echo >&2 "ERROR: $1" 
    exit 1
}

TARGET_DIR=''
QUEUEDIR='%QUEUEDIR%'

# Handle the command line parameters
while getopts d:hq:tz: OPT; do
    case "$OPT" in
        d) 
            TARGETDIR="$OPTARG"
            ;;
        h)
            usage
            exit
            ;;
        q)
            QUEUEDIR="$OPTARG"
            ;;
        t) ;;
        z)
            # This is for the test code
            DEBUG_FLAG="$OPTARG"
            ;;
        ?) ;;
    esac
done

if [ -z "$2" ] ; then
    echo >&2 'ERROR: missing arguments'
    usage >&1
    exit 1
fi


#BEGIN_DEBUG
# Print out the current variable
if [ -n "$DEBUG_FLAG" ] ; then
    case "$DEBUG_FLAG" in 
        'TARGETDIR')
            echo "$TARGETDIR"
            exit
            ;;
        'QUEUEDIR')
            echo "$QUEUEDIR"
            exit
            ;;
    esac
fi
#END_DEBUG


