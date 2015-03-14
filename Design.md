# Design Decisions #
These are various design decisions encountered in the development and the reasoning behind the route that we took.

## stdout and stderr Interpolation ##
Consider the following shell snippet:

```
echo stdout; sleep 1; echo stderr 1>&2; sleep 1; echo stdout2
```

If you run this line from the shell, here the output you will see (with one second pauses between the lines):

```
stdout
stderr
stdout2
```

Cronwatch could capture the output from this snippet in three ways:

  1. Separate stdout and stderr and handle the two separately
  1. Somehow poll stdout and stderr to try to get a chronologically correct output
  1. Combine stdout and stderr and handle them together

In the first scenario, cronwatch waits for the process to finish and present the user with two separate sets of output something like this:

```
Standard out:
stdout
stdout2

Standard error:
stderr
```

The user would be able to run a different set of rules on stdout and stderr. For example, only the word "error" in stdout might trigger an error, but any output to stderr would always trigger an error.

This approach presents one main problem: Anything from stderr is shown out of context. While the lack of context might not always be bad, it often can make debugging challenging.

In the second scenario, cronwatch would constantly watch stdout and stderr and interpolate them for the final output while keeping them separate for the rules. This scenario might seem ideal, but presents all sorts of performance and complexity problems. Even if we were able to get it almost right, it inherently has a race condition that would make slight changes in order possible.

Finally, by redirecting stderr to stdout we can be sure that the order of output is correct. However, we lose the ability to distinguish the two. Cron and at seem to use this method, since any output whatsoever is considered a "reportable" event.

This decision was a hard one. Ideally cronwatch would allow different rules for stdout and stderr, but would offer a chronologically correct interpolation without causing performance issues. Maybe in a later version we can investigate this possibility, but for now, we will redirect stderr to stdout. If there is a need, we could add the option to separate the two.