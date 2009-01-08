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

# Print an error message and exit
error () {
    echo >&2 "ERROR: $1" 
    exit 1
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


#BEGIN_DEBUG
# Print out the current variables
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
#END_DEBUG

# Check to make sure the options are good
if [ -n "$CONFIGFILE" -a ! -r "$CONFIGFILE" ] ; then
    error "could not read config file $CONFIGFILE"
fi

if [ ! -w "$QUEUEDIR" ] ; then
    error "could not write to queue directory $QUEUEDIR"
fi

# Make sure the executable is runnable
if [ ! -x "$1" ] ; then
    error "could not run $1"
fi

# Generate a (hopefully) unique directory for the queue directory
UNIQUEDIR=`date +%Y%m%d%H%M%S_$$`

if [ ! "$?" = '0' ] ; then
    error 'could not generate date'
fi

# Make sure the directory and lock file don't already exist
# (this should never happen)
if [ -e "$QUEUEDIR/$UNIQUEDIR.lock" -o -e "$QUEUEDIR/$UNIQUEDIR" ] ; then
    error "unique directory $UNIQUEDIR was not unique"
fi

# Create the queue directory
mkdir "$QUEUEDIR/$UNIQUEDIR"

if [ ! "$?" = '0' ] ; then
    error "could not create queue directory $QUEUEDIR/$UNIQUEDIR"
fi

PROG="$1"
shift 1

# Run the program
env - "$PROG" "$@" > "$QUEUEDIR/$UNIQUEDIR/output" 2>&1

RETURNVAL="$?"

