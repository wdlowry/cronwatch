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

TARGETDIR=''
QUEUEDIR='%QUEUEDIR%'
TESTFLAG=''

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
        t)
            TESTFLAG='1'
            ;;
        z)
            # This is for the test code
            DEBUG_FLAG="$OPTARG"
            ;;
        ?) ;;
    esac
done

shift `expr $OPTIND - 1`

# Check for necessary arguments
if [ -z "$2" ] ; then
    echo >&2 'ERROR: missing arguments'
    usage >&1
    exit 1
fi

TARGETUSER="$1"
TARGETHOST="$2"


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

# Make sure the queue directory is readable
if [ ! -r "$QUEUEDIR" ] ; then
    error "could not read from queue directory $QUEUEDIR"
fi

# Set the target
TARGET="$TARGETUSER@$TARGETHOST:"

if [ -n "$TARGETDIR" ] ; then
    TARGET="$TARGET$TARGETDIR/"
fi

# Test the connection
if [ "$TESTFLAG" = '1' ] ; then
    touch "$QUEUEDIR/test_upload"
    if [ ! "$?" = '0' ] ; then
        error "could not create test upload file $QUEUEDIR/test_upload"
    fi

    scp -B -q -r "$QUEUEDIR/test_upload" "$TARGET"
    
    if [ ! "$?" = '0' ] ; then
        error "could not copy to $TARGETUSER@$TARGETHOST:$TARGETDIR"
    fi

    echo 'Connection successful!'
    
    exit
fi

# Generate unique directory name
UNIQUEPREFIX="`hostname`_$$_"
cd "$QUEUEDIR"

# Go through the queue dir
for FILE in * ; do
    # Only handle directories
    if [ -d "$FILE" ] ; then

        # Ignore locked files
        if [ ! -r "$FILE.lock" ] ; then
            scp -B -q -r "$FILE" "$TARGET$UNIQUEPREFIX$FILE"
            
            if [ ! "$?" = '0' ] ; then
                error "could not copy to $TARGETUSER@$TARGETHOST:$TARGETDIR"
            fi

            touch "$FILE.complete"

            if [ ! "$?" = '0' ] ; then
                error "could not create $QUEUEDIR/$FILE.complete"
            fi

            # Copy file to show that the transfer was completed successfully
            scp -B -q -r "$FILE.complete" "$TARGET$UNIQUEPREFIX$FILE.complete"

            if [ ! "$?" = '0' ] ; then
                rm -rf "$FILE.complete"
                error "could not copy transfer-complete file to $TARGETUSER@$TARGETHOST:$TARGETDIR"
            fi


            # Clean up
            rm -rf "$FILE"
            rm -rf "$FILE.complete"
        fi
    fi
done
