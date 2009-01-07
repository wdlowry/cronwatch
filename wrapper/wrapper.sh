#!/bin/sh
# $Id$
# vim:ft=sh:sw=4:sta:et
#
# wrapper - Capture output from cron jobs and store it for processing
#
# Written by David Lowry
# Released under the GPL version 2
#

# Print out the usage
usage () {
    cat << EOF
usage: $0 [options] executable [arguments]

options:
  -c                    config file
  -h                    this help message
  -q                    queue directory
  -u                    unique job name
EOF
}

# Check for necessary options
if [ -z "$1" ] ; then
    echo >&2 'ERROR: missing argument'
    usage >&2
    exit 1
fi

# Set option variables
CONFIGFILE=''
QUEUEDIR='%QUEUEDIR%'
UNIQUEID=''

# Handle the command line options
while getopts c:hq:u:z: OPT; do
    case "$OPT" in
        c)
            CONFIGFILE="$OPTARG"
            ;;
        h)
            usage
            exit
            ;;
        q)
            QUEUEDIR="$OPTARG"
            ;;
        u)
            UNIQUEID="$OPTARG"
            ;;
        z)
            # This is for the test code
            DEBUG_FLAG="$OPTARG"
            ;;
        ?) ;;
    esac
done

shift "$((OPTIND - 1))"

# Debugging code for test cases.
if [ -n "$DEBUG_FLAG" ] ; then
    case "$DEBUG_FLAG" in
        'CONFIGFILE')
            echo "$CONFIGFILE"
            ;;
        'QUEUEDIR')
            echo "$QUEUEDIR"
            ;;
        'UNIQUEID')
            echo "$UNIQUEID"
            ;;
    esac
    exit
fi
