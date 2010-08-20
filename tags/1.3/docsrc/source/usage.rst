*****
Usage
*****

.. _defaults:

Default Behavior
================
In its default configuration, cronwatch simply executes the specified command
and handles any abnormal exit code or output by mailing it to the current user.
The :ref:`configuration options <config>` allow the user to control where that
output is sent and what is considered "abnormal."

Installation
============
The easiest way to install cronwatch is `easy_install
<http://pypi.python.org/pypi/setuptools>`_::

    easy_install cronwatch

You can also download it and install it manually.


  #. Download `ConfigObj <http://pypi.python.org/pypi/configobj/>`_ and install 
     it::

         wget http://pypi.python.org/packages/source/c/configobj/configobj-4.7.2.tar.gz
         tar xzf configobj-4.7.2.tar.gz
         cd configobj-4.7.2
         python setup.py install

  #. Download `cronwatch <http://code.google.com/p/cronwatch/downloads/list>`_
  #. Unpack it::

         tar xzf cronwatch-1.3.tar.gz
    
  #. Install it using setup.py::

         cd cronwatch-1.3
         python setup.py install

Sample Usage
============
cronwatch can be run from the command line to test that everything is set up
correctly::

    # cronwatch /bin/true

Some errors are severe enough to warrant an immediate error::

    # cronwatch /bin/truely
    ERROR: could not run /bin/truely: [Errno 2] No such file or directory

Typically, cronwatch will be executed from a crontab. You'll need to make sure
that you either specify the correct PATH for cronwatch or that you use the full
path name for cronwatch::

    PATH=/usr/local/bin:/usr/bin:/bin
    30 14 * * * cronwatch /bin/echo time for coffee

You can also specify a configuration file and tags from the command line (these
concepts will be explained later)::

    30 14 * * * cronwatch -c /etc/cronwatch/coffee.conf -t coffee /bin/echo time for coffee

Now that you know how to run cronwatch, look at the
:ref:`configuration documentation <config>` to see how to configure cronwatch to
handle certain output.

