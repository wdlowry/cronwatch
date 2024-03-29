.. _config:

*********************
Configuring cronwatch
*********************


Configuration File Location
===========================
By default, cronwatch will check if /etc/cronwatch.conf exists, and if it does,
use it as the configuration file. If this file does not exist, cronwatch will
behave essentially as if it were cron (see :ref:`defaults`). In this scenario,
it will handle any output or non-zero exit code as an error and send an e-mail
to the user that called cronwatch.

If a file is specified on the command line with the ``-c`` option, then this
file is used as the configuration file. If this file doesn't exist, cronwatch
will fail with an error.

Tags
====
cronwatch allows you to put mutliple configurations in the same configuration
file. It determines which configuration section to use using a feature called
"tags." By default, the tag is determined by the basename of the executable.
For example, if you are running the following cronwatch command::

    cronwatch /my/very/special/script.sh

then the tag will be ``script.sh``. However, if you supply a tag on the command
line using the ``-t`` option, then that tag argument will override the default
tag. For example, in this command line::

    cronwatch -t generic /my/very/special/script.sh

the tag is ``generic``.

Sections
========
conwatch allows you to specify multiple configurations in the same
configuration file.  Consider the following configuration file::

    [_default_]
    blacklist = ERROR

    [myscript]
    blacklist = really bad error

In this case, the ``[myscript]`` section will be used only if the tag is
``myscript``, like in these two examples::

    cronwatch /usr/local/bin/myscript
    cronwatch -t myscript /my/very/special/script.sh

Any other tag would make cronwatch use the ``[_default_]`` section. In the
event that there is no ``[_default_]`` section and a suitable section cannot be
found, cronwatch will use the :ref:`defaults <defaults>`.

Regular Expressions
===================
cronwatch uses the Python ``re`` module for regular expression matching.
Python's ``re`` module uses a similar syntax to PCRE. See `the module
documentation
<http://docs.python.org/library/re.html#regular-expression-syntax>`_ for more
details.

One little tidbit: To make a regular expression case insensitive, use the string
``(?i)`` somewhere in the regular expressions.

.. _options:

Options
=======
cronwatch offers many different configuration options that allow the user to
modify what it reports and where it sends those reports.

cronwatch supports these configuration options:

+-----------------------+-----------------------------------------------------+
| Name                  | Default Value                                       |
+=======================+=====================================================+
| :ref:`required`       | Not set                                             |
+-----------------------+-----------------------------------------------------+
| :ref:`blacklist`      | ``.*`` (See :ref:`blacklist` for more information)  |
+-----------------------+-----------------------------------------------------+
| :ref:`whitelist`      | Not set                                             |
+-----------------------+-----------------------------------------------------+
| :ref:`exit_codes`     | ``0``                                               |
+-----------------------|-----------------------------------------------------+
| :ref:`preamble_file`  | Not set                                             |
+-----------------------+-----------------------------------------------------+
| :ref:`email_to`       | The username of the current user                    |
+-----------------------+-----------------------------------------------------+
| :ref:`email_from`     | The username and hostname of the current user in    |
|                       | the ``username@hostname.domain.tld`` format         |
+-----------------------+-----------------------------------------------------+
| :ref:`email_maxsize`  | ``102400``                                          |
+-----------------------+-----------------------------------------------------+
| :ref:`email_success`  | ``False``                                           |
+-----------------------+-----------------------------------------------------+
| :ref:`email_sendmail` | ``/usr/lib/sendmail``                               |
+-----------------------+-----------------------------------------------------+
| :ref:`logfile`        | Not set                                             |
+-----------------------+-----------------------------------------------------+

.. _required:

required
--------
This setting specifies a regular expression or a list of regular expressions
that must be matched in the output for the job to be considered successful. By
default it is not set.

Examples::

    required = success
    required = '''success''', '''read [0-9] bytes of data''', '''wrote data'''

.. _blacklist:

blacklist
---------
This setting is a regular expression or a list of regular expressions that
must not match lines in the output. If they are found, cronwatch will 
flag an error.

By default, if ``required`` and ``whitelist`` are *not* set, then blacklist is 
``.*``. Otherwise, ``blacklist`` is not set unless it is specified in the 
configuration file.

Examples::

    blacklist = error
    blacklist = bad error, worse error, 'really, really bad error'

.. _whitelist:

whitelist
---------
This setting is a regular expression or a list of regular expressions that are
allowed in the output. If a line of output does not match one of the
``whitelist`` regular expressions, then the job will complete unsuccessfully.
By default it is not set.

If both ``whitelist`` and ``blacklist`` are specified, then the output is first
tested against whitelist. If it passes, it is then tested against blacklist.
For example, if whitelist is ``success`` and blacklist is ``not`` then ``not
successful`` will match both and thus be marked as an error.

Examples::

    whitelist = success
    whitelist = success, read data, 'read much, much data'

.. _exit_codes:

exit_codes
----------
This settings is a list of integers that tells cronwatch which exit codes are
acceptable. Other codes will result in an error. The default is `0`.

Example::

    exit_code = 0, 1

.. _preamble_file:

preamble_file
-------------
This setting inserts the contents of a text file into the e-mail and log file.
The contents of this file are put in right before the output of the command.

Example::

    preamble_file = /path/to/text.txt

.. _email_to:

email_to
--------
This setting specifies where to e-mail output from the job. The default setting
is to send mail to the current user's username.

Examples::

    email_to = root
    email_to = user@example.com

.. _email_from:

email_from
----------
This setting sets the "From" address for the e-mail. By default, this will be
the username of the current user.

Examples::
    
    email_from = root
    email_from = user@example.com

.. _email_maxsize:

email_maxsize
-------------
This setting limits the size of e-mails cronwatch sends. The default value is
``102400``. If the entire output should be sent, then ``email_maxlines`` should
be set to ``-1``.

*Caution*: If you don't know the maximum size of the output, it would be better to set a maximum size just in case the output gets really large.

Examples::

    email_maxsize = -1
    email_maxsize = 1024


.. _email_success:

email_success
-------------
In the default configuration, cronwatch only sends e-mail when there is an
error (e.g. the blacklist matches a line of output). This settings tells
cronwatch to always send e-mail, even if the job was successful.

Example::
    
    email_success = on

.. _email_sendmail:

email_sendmail
--------------
This settings tells cronwatch where to find the sendmail program and what
parameters to use when calling sendmail. It defaults to ``/usr/lib/sendmail``. 

Examples::

    email_sendmail = /usr/local/bin/sendmail
    email_sendmail = /usr/lib/sendmail -t

.. _logfile:

logfile
-------
This setting makes cronwatch use a log file for the job's output. By default,
it is not set and no logfile is written.

When determining the log file name, cronwatch uses Python's `strftime function
<http://docs.python.org/library/datetime.html#strftime-strptime-behavior>`_ to
add date and time information.

Examples::

    logfile = /var/log/cronwatch/job.log
    logfile = /var/log/cronwatch/job-%Y%m%d%h%M.log

Example Configuration File
==========================
Here is an example configuration file. See the configuration options above for
more information.

Example configuration file::

    # These defaults are applied when another section doesn't apply
    [_defaults_]

    # Send an e-mail to root on the local machine when something messes up
    email_to = root

    # Truncate the e-mail if it's bigger than 1M
    email_maxsize = 1048576

    # The exit code must either be 0 or 10
    exit_codes = 0, 10

    [log_cleanup]
    # Make sure this regular expression is in the output
    required = [0-9]+ log file\(s\) successfully rotated.

    # Blacklist any line with error (case-insensitive) in it
    # Also blacklist lines that begin with "Could not ..."
    blacklist = (?i)error, '^Could not open, try again'
    
    logfile = /var/log/log_cleanup-%Y%m%d%h%m.log

