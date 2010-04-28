GREEN, BROWN, BLUE, MAGENTA, CYAN, WHITE = range(32, 38)

def colorize(s, color=CYAN):
	return "".join((chr(0033), '[1;%sm' % color, s, chr(0033), '[m'))

def tracer(frame, event, arg):
    if event in ('c_call', 'c_return', 'c_exception'):
        return tracer

    if frame.f_code.co_name in ("<module>", '__getattr__', '__init__', '<genexpr>', 'tofnamemoduleline', 'showstack', 'is_id_field', 'is_ids_field', 'convert_kv_pair', 'convert'):
        return tracer

    # event is call or return (for setprofile)
    line_nr = frame.f_code.co_firstlineno
    fn_name = frame.f_code.co_name
    filename = frame.f_code.co_filename

    if filename.startswith('/usr') or filename.startswith('/var/lib'):
        return tracer

    excluded_files = (
        'util/yelpy.py',
        'yelp/models/types.py',
        'yelp/snappy/__init__.py',
        'util/crypto.py',
        'logic/encapsulation.py',
        'logic/adapter.py',
        'yelp/util/signals.py',
        'util/applog.py',
    )

    for file in excluded_files:
        if filename.endswith(file):
            return tracer

    stack_size = len(inspect.stack())

    _, _, _, argvalues = inspect.getargvalues(frame)
    if 'pattern' in argvalues:
        return tracer

    try:
        args = inspect.formatargvalues(*inspect.getargvalues(frame))
    except Exception, e:
        print e
        return tracer

    first_part = " ".join(("|" * stack_size, event, fn_name, '[%s +%s]' % (colorize(filename), line_nr))).ljust(120, '.')
    print first_part, args[:160]

    return tracer

