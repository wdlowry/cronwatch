*****************************
Overview of Need and Features
*****************************


Need
====
The traditional UNIX crond handles scheduling and executing jobs very well.
However, it handles abnormal program runs, output to stderr for example, very
poorly. cronwatch seeks to fill that gap by capturing and acting upon the
output and exit codes of jobs executed by cron.

In its default configuration, it acts much like standard cron: It considers any
output or non-zero exit code to be an error and e-mails the owner of the
crontab. The user can adjust the configuration to handle output differently and
alert other e-mail addresses. 

Features
========
  * Can ensure that certain regular expressions exist in the output to 
    consider a job successful
  * Can determines the success or failure of a job based on output whitelists
    and blacklists
  * Can handle multiple valid exit codes
  * Allows the recipient and sender e-mail addresses to be changed
  * Can limit the size of the e-mail to avoid extremely large e-mails for jobs 
    with lots of output 
  * Can write the output to a log file

