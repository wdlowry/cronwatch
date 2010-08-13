.. _config:

*********************
Configuring cronwatch
*********************


Configuration File Location
===========================
By default, cronwatch will check if /etc/cronwatch.conf exists, and if it does,
use it as the configuration file. If this file does not exist, cronwatch will
behave essentially as if it were cron (see the defaults below). In this
scenario, it will handle any output or non-zero exit code as an error and send
an e-mail to the user that called cronwatch.

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
line using the ``-t`` option, then that tag argument will override the tag. For example, in this command line::

    cronwatch -t generic /my/very/special/script.sh

the tag is ``generic``.

Sections
========
conwatch allows you to specify multiple configurations in the same configurationfile.  Consider the following configuration file::

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

Options
=======
cronwatch offers many different configuration options that allow the user to
modify what it reports and where it sends those reports.




= Configuration Options =
cronwatch understands these configuration options.

== required ==
|| *Name:* || `required` ||
|| *Default Value:* || None ||
|| *Description:* || A regular expression or a list of regular expressions that must be found in the output for the job to be considered successful. ||

== blacklist ===
|| *Name:* || `blacklist` ||
|| *Default Value:* || `.*` ||
|| *Description:* || A regular expression or a list of regular expressions that will result in an error if found in the output. ||

== whitelist ==
|| *Name:* || `whitelist` ||
|| *Default Value:* || None ||
|| *Description:* || A regular expression or a list of regular expressions that if are not matched will result in an error. ||

If whitelist is specified, then the every line of output is matches against the regular expression(s). If it does not match, then cronwatch will flag the output as an error.

If both whitelist and blacklist are specified, then the output is first tested against whitelist. If it passes, it is then tested against blacklist. For example, if whitelist is `success` and blacklist is `not` then `not successful` will match both and thus be marked as an error.

== exit_codes ==
|| *Name:* || `exit_codes` ||
|| *Default Value:* || `0` ||
|| *Description:* || A list of acceptable error code. Other error codes will result in an error. ||

== email_to ==
|| *Name:* || `email_to` ||
|| *Default Value:* || None ||
|| *Description:* || An e-mail address to which to send output. This address can be a local account, for example, `root`, the default. If this setting is not specified (the default), then it will be generate in the format: <username> ||

== email_from ==
|| *Name:* || `email_from` ||
|| *Default Value:* || None ||
|| *Description:* || An e-mail address from which to send output. If this setting is not specified (the default), then it will be generated in the format: User Name <username@hostname> ||


== email_maxsize ==
|| *Name:* || `email_maxsize` ||
|| *Default Value:* || `4096` ||
|| *Description:* || The maximum size of output to send in an e-mail. If everything should be sent, then `email_maxlines` should be set to -1 ||

*Caution*: If you don't know the maximum size of the output, it would be better to set a maximum size just in case the output gets really large.

== email_success ==
|| *Name:* || `email_success` ||
|| *Default Value:* || `false` ||
|| *Description:* || Determines whether an e-mail should be sent if the job was successful.||

== email_sendmail ==
|| *Name:* || `email_sendmail` ||
|| *Default Value:* || `/usr/lib/sendmail` ||
|| *Description:* || The location and parameters for sendmail.||

== logfile ==
|| *Name:* || `logfile` ||
|| *Default Value:* || None ||
|| *Description:* || The file name for the log file. ||

When determining the log file name, cronwatch first replaces `%TAG%` with the current tag and then uses Python's [http://docs.python.org/library/datetime.html#strftime-strptime-behavior strftime] to add date and time information. For example, `/var/log/cronwatch-%TAG%-%Y%m%d%h%M.log` would be evaluated to something like `/var/log/cronwatch-myjob-201001010952.log`.

= Example Configuration File =
Here is an example configuration file. See the configuration options below for more information.
{{{
# These defaults are applied to the other sections
[defaults]

# Send an e-mail to root on the local machine when something messes up
email_to = root

# Truncate the e-mail if it's bigger than 1M
email_maxsize = 1048576

# The exit code must either be 0 or 10
exit_codes = 0
exit_code = 10

[log_cleanup]
# Make sure this regular expression is in the output
required = [0-9]+ log file\(s\) successfully rotated.

# Both of 
blacklist = (?i)error
blacklist = ^Could not open
logfile = /var/log/%TAG%-%Y%m%d%h%m.log
}}}

= Regular Expressions =
cronwatch uses the Python re module for regular expression matching. Python's re module uses a similar syntax to PCRE. See http://docs.python.org/library/re.html#regular-expression-syntax for more details.
