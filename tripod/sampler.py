import datetime as dt
import inspect
import linecache
import os
import pprint
import sys
import tempfile
import thread

from timer import Timer


class SafePrettyPrinter(pprint.PrettyPrinter, object):
    def format(self, obj, context, maxlevels, level):
        try:
            return super(SafePrettyPrinter, self).format(
                obj, context, maxlevels, level)
        except Exception:
            return object.__repr__(obj)[:-1] + ' (bad repr)>', True, False


def spformat(obj, depth=None):
    return SafePrettyPrinter(indent=1, width=76, depth=depth).pformat(obj)


def formatvalue(v):
    s = spformat(v, depth=1).replace('\n', '')
    if len(s) > 250:
        s = object.__repr__(v)[:-1] + ' (really long repr)>'
    return '=' + s


def stack(f, with_locals=False):
    limit = getattr(sys, 'tracebacklimit', None)

    frames = []
    n = 0
    while f is not None and (limit is None or n < limit):
        lineno, co = f.f_lineno, f.f_code
        name, filename = co.co_name, co.co_filename
        args = inspect.getargvalues(f)

        linecache.checkcache(filename)
        line = linecache.getline(filename, lineno, f.f_globals)
        if line:
            line = line.strip()
        else:
            line = None

        frames.append((filename, lineno, name, line, f.f_locals, args))
        f = f.f_back
        n += 1
    frames.reverse()

    out = []
    for filename, lineno, name, line, localvars, args in frames:
        out.append('  File "%s", line %d, in %s' % (filename, lineno, name))
        if line:
            out.append('    %s' % line.strip())

        if with_locals:
            args = inspect.formatargvalues(formatvalue=formatvalue, *args)
            out.append('\n      Arguments: %s%s' % (name, args))

        if with_locals and localvars:
            out.append('      Local variables:\n')
            try:
                reprs = spformat(localvars)
            except Exception:
                reprs = "failed to format local variables"
            out += ['      ' + l for l in reprs.splitlines()]
            out.append('')
    return '\n'.join(out)


def peek(fd, thread_id, started):
    frame = sys._current_frames()[thread_id]

    output = stack(frame, with_locals=False)
    output += '\n\n'

    output += 'Full backtrace with local variables:'
    output += '\n\n'
    output += stack(frame, with_locals=True)
    output += '\n\n'
    output += ('-' * 80) + '\n\n'

    output = output.encode('utf-8')

    os.write(fd, output)


def main():
    interval = 5

    if len(sys.argv) > 1:
        script_path = sys.argv[1]
        sys.argv = sys.argv[1:]
    else:
        print >> sys.stderr, "usage: python -m tripod.sampler ./script_path.py"
        print >> sys.stderr, "(Default interval: %f seconds. Override with TRIPOD_INTERVAL env var)" % interval
        sys.exit(1)

    interval = float(os.environ.get("TRIPOD_INTERVAL", interval))

    timer = Timer()
    timer.setDaemon(True)
    timer.start()

    # dump to file:
    fd, fn = tempfile.mkstemp(prefix='slow_process_', suffix='.log', dir='/tmp')

    print >> sys.stderr, "[Tripod] Sampling every %f seconds" % interval
    print >> sys.stderr, "[Tripod] Writing output to:", fn

    timer.run_later(peek, interval, fd, thread.get_ident(), dt.datetime.utcnow())

    exit_code = 0
    try:
        with open(script_path) as f:
            global __file__
            __file__ = script_path
            exec f.read() in globals(), globals()
    except SystemExit, e:
        exit_code = e.code
    finally:
        os.close(fd)

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
