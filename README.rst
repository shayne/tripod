====================================================
Tripod - Slow Script Watchdog
====================================================


Overview
--------

Tripod is a module that samples running scripts, logging tracebacks to a temp file.

Most of the code was brought over from the `Django watchdog middleware project, Dogslow`_.

.. _Django watchdog middleware project, Dogslow: https://bitbucket.org/evzijst/dogslow


Installation
------------

Install tripod::

    $ pip install tripod


Configuration
-------------

You can use the following environmental variables to adjust the sampler::

    # Log traceback of running script every 5 seconds
    TRIPOD_INTERVAL = 5


Usage
-----

Run tripod::

    $ python -m tripod.sampler ./some_script.py
    [Tripod] Sampling every 5.000000 seconds
    [Tripod] Writing output to: /tmp/slow_process_tkM6Rt.log

Every 5 seconds the watchdog is activated and takes a peek at the script's
stack and appends the backtrace (including all local stack variables) to the
log file.

Every stack is appended to the log file and looks like this::


    File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/runpy.py", line 162, in _run_module_as_main
        "__main__", fname, loader, pkg_name)
    File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/runpy.py", line 72, in _run_code
        exec code in run_globals
    File "/Users/shayne/Code/tripod/tripod/sampler.py", line 128, in <module>
        main()
    File "/Users/shayne/Code/tripod/tripod/sampler.py", line 118, in main
        exec f.read() in globals(), globals()
    File "<string>", line 5, in <module>
    File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/socket.py", line 351, in read
        data = self._sock.recv(rbufsize)
    File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/httplib.py", line 553, in read
        s = self.fp.read(amt)
    File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/socket.py", line 380, in read
        data = self._sock.recv(left)

    Full backtrace with local variables:

    File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/runpy.py", line 162, in _run_module_as_main
        "__main__", fname, loader, pkg_name)

        Arguments: _run_module_as_main(mod_name='tripod.sampler', alter_argv=1)
        Local variables:

        {'alter_argv': 1,
        'code': <code object <module> at 0x10ba09a30, file "/Users/shayne/Code/tripod/tripod/sampler.py", line 1>,
        'fname': '/Users/shayne/Code/tripod/tripod/sampler.py',
        'loader': <pkgutil.ImpLoader instance at 0x10ba0a368>,
        'main_globals': {'SafePrettyPrinter': <class '__main__.SafePrettyPrinter'>,
                            'Timer': <class 'tripod.timer.Timer'>,
                            '__builtins__': <module '__builtin__' (built-in)>,
                            '__doc__': None,
                            '__file__': 'slow.py',
                            '__loader__': <pkgutil.ImpLoader instance at 0x10ba0a368>,
                            '__name__': '__main__',
                            '__package__': 'tripod',
                            'dt': <module 'datetime' from '/Users/shayne/pyenv/lib/python2.7/lib-dynload/datetime.so'>,
                            'f': <addinfourl at 4495809568 whose fp = <socket._fileobject object at 0x10bac70d0>>,
                            'formatvalue': <function formatvalue at 0x10bac1320>,
                            'inspect': <module 'inspect' from '/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/inspect.py'>,
                            'linecache': <module 'linecache' from '/Users/shayne/pyenv/lib/python2.7/linecache.pyc'>,
                            'main': <function main at 0x10bac1488>,
                            'os': <module 'os' from '/Users/shayne/pyenv/lib/python2.7/os.pyc'>,
                            'peek': <function peek at 0x10bac1410>,
                            'pprint': <module 'pprint' from '/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/pprint.py'>,
                            'spformat': <function spformat at 0x10ba649b0>,
                            'stack': <function stack at 0x10bac1398>,
                            'sys': <module 'sys' (built-in)>,
                            'tempfile': <module 'tempfile' from '/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/tempfile.pyc'>,
                            'thread': <module 'thread' (built-in)>,
                            'urllib2': <module 'urllib2' from '/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/urllib2.pyc'>},
        'mod_name': 'tripod.sampler',
        'pkg_name': 'tripod'}

    File "/System/Library/Frameworks/Python.framework/Versions/2.7/lib/python2.7/runpy.py", line 72, in _run_code
        exec code in run_globals

        Arguments: _run_code(code=<code object <module> at 0x10ba09a30, file "/Users/shayne/Code/tripod/tripod/sampler.py", line 1>, run_globals=<dict object at 0x7f9812c1dc40 (really long repr)>, init_globals=None, mod_name='__main__', mod_fname='/Users/shayne/Code/tripod/tripod/sampler.py', mod_loader=<pkgutil.ImpLoader instance at 0x10ba0a368>, pkg_name='tripod')
        Local variables:

        {'code': <code object <module> at 0x10ba09a30, file "/Users/shayne/Code/tripod/tripod/sampler.py", line 1>,
        'init_globals': None,
        'mod_fname': '/Users/shayne/Code/tripod/tripod/sampler.py',
        'mod_loader': <pkgutil.ImpLoader instance at 0x10ba0a368>,
        'mod_name': '__main__',

      ...loads more...

The example above shows that the request thread was blocked in
``f.read()`` at the time ``tripod`` took its snapshot.

Note that ``tripod`` only takes a peek at the thread's stack. It does not
interrupt the script, or influence it in any other way.


Caveats
-------

Tripod, like Dogslow uses multithreading. It has a single background thread that handles the
timer timeouts and takes the tracebacks, so that the original script
threads are not interrupted. This has some consequences.


Multithreading and the GIL
~~~~~~~~~~~~~~~~~~~~~~~~~~

In cPython, the GIL (Global Interpreter Lock) prevents multiple threads from
executing Python code simultaneously. Only when a thread explicitly releases
its lock on the GIL, can a second thread run.

Releasing the GIL is done automatically whenever a Python program makes
blocking calls outside of the interpreter, for example when doing IO.

For ``tripod`` this means that it can only reliably sample scripts that
are slow because they are doing IO, calling sleep or busy waiting to acquire
locks themselves.

In most cases this is fine. A scenario where cPython's GIL is problematic
is when the request's thread hits an infinite loop in Python code
(or legitimate Python that is extremely expensive and takes a long time
to execute), never releasing the GIL. Even though ``tripod``'s watchdog
timer does become runnable, it cannot log the stack.


Co-routines and Greenlets
~~~~~~~~~~~~~~~~~~~~~~~~~

``Tripod`` is intended for use in a synchronous configuration. A
process that uses dedicated threads (or single-threaded processes).

When running with a "co-routines framework" where multiple requests are served
concurrently by one thread, backtraces might become nonsensical.
