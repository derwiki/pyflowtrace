"""To use:
import sys
import pyflowtrace
sys.setprofile(pyflowtrace.tracer)

Put that code where you want to begin your trace
I recommend after imports are done to avoid clutter.

`excluded_files` exists for you to filter out modules
that don't provide any useful information. Same goes
for `excluded_functions`.
"""

import inspect

has_custom = False
try:
    import custom
    has_custom = True
except ImportError:
    pass


logfile = open("trace.flw", "w+")
GREEN, BROWN, BLUE, MAGENTA, CYAN, WHITE = range(32, 38)


def colorize(s, color=CYAN):
    return s
    # return "".join((chr(0033), '[1;%sm' % color, s, chr(0033), '[m'))


if has_custom and hasattr(custom, 'cursor_variables'):
    cursor_variables = custom.cursor_variables
else:
    cursor_variables = ('cursor', 'batch_cursor', 'rocursor')


def tracer(frame, event, arg):
    if event in ('c_call', 'c_return', 'c_exception'):
        return tracer

    # event is call or return (for setprofile)
    line_nr = frame.f_code.co_firstlineno
    fn_name = frame.f_code.co_name
    filename = frame.f_code.co_filename

    excluded_functions = (
      '<genexpr>',
      '<module>',
      '__getattr__',
      '__init__',
      '_remove',
      'convert',
      'convert_kv_pair',
      'is_id_field',
      'is_ids_field',
      'showstack',
      'tofnamemoduleline',
    )

    if frame.f_code.co_name in excluded_functions:
        return tracer

    # exclude python libraries and stick to application code
    if 'python2.7' in filename:
        return tracer

    # ignore builtin and library calls
    if filename.startswith('/usr') or filename.startswith('/var/lib'):
        return tracer

    if has_custom and hasattr(custom, 'file_prefix_ignore'):
        if filename.startswith(custom.file_prefix_ignore):
            filename = filename[len(custom.file_prefix_ignore):]

    # set nuisance files here, will be skipped
    if has_custom and hasattr(custom, 'excluded_files'):
        excluded_files = custom.excluded_files
    else:
        excluded_files = ()

    for file in excluded_files:
        if filename.endswith(file):
            return tracer

    if hasattr(inspect, 'stack'):
        stack_size = len(inspect.stack())
    else:
        raise Exception("Add {} to `excluded_functions`".format(fn_name))

    # formatargvalues chokes on things not having self.data sometimes
    try:
        raw_args = inspect.getargvalues(frame)
        post_args = []
        # TODO abstract out arg processing rules
        for arg in raw_args:
            if isinstance(arg, dict):
                arg = dict([(item, value) if item not in cursor_variables else (
                    item, (value.connection.name, value)) for item, value in arg.items()])
            post_args.append(arg)
        args = inspect.formatargvalues(*post_args)
    except Exception, e:
        print e
        return tracer

    FUNCTION_COLS = 90

    stack_ruler = "".join((str(i) for i in xrange(0, 9))) * 4
    function_section = " ".join((stack_ruler[:stack_size], event, fn_name, '[%s +%s]' % (
        colorize(filename), line_nr))).ljust(FUNCTION_COLS, '.')

    if event == "call":
        param_section = "params: %s" % args
    elif event == "return":
        param_section = "return: %s" % arg

    buffer = "%s %s\n" % (function_section, param_section)
    logfile.write(buffer)
    logfile.flush()

    return tracer
