"""To use:
import sys
import pyflowtrace
sys.setprofile(pyflowtrace.tracer)

Put that code where you want to begin your trace
I recommend after imports are done to avoid clutter.

'excluded_files' exists for you to filter out modules
that don't provide any useful information. Same goes
for 

"""

import inspect
import custom

logfile = open("trace.flw", "w+")
GREEN, BROWN, BLUE, MAGENTA, CYAN, WHITE = range(32, 38)

def colorize(s, color=CYAN):
	return "".join((chr(0033), '[1;%sm' % color, s, chr(0033), '[m'))

def tracer(frame, event, arg):
	if event in ('c_call', 'c_return', 'c_exception'):
		return tracer

	excluded_functions = ("<module>", '__getattr__', '__init__', '<genexpr>', 'tofnamemoduleline', 'showstack', 'is_id_field', 'is_ids_field', 'convert_kv_pair', 'convert')
	if frame.f_code.co_name in excluded_functions:
		return tracer

	# event is call or return (for setprofile)
	line_nr = frame.f_code.co_firstlineno
	fn_name = frame.f_code.co_name
	filename = frame.f_code.co_filename

	# ignore builtin and library calls
	if filename.startswith('/usr') or filename.startswith('/var/lib'):
		return tracer

	# set nuisance files here, will be skipped
	if hasattr(custom, "excluded_files"):
		excluded_files = custom.excluded_files
	else:
	excluded_files = ()

	for file in excluded_files:
		if filename.endswith(file):
			return tracer

	stack_size = len(inspect.stack())

	# formatargvalues chokes on things not having self.data sometimes
	try:
		args = inspect.formatargvalues(*inspect.getargvalues(frame))
	except Exception, e:
		print e
		return tracer

	FUNCTION_COLS = 120
	PARAM_COLS = 260

	function_section = " ".join(("|" * stack_size, event, fn_name, '[%s +%s]' % (colorize(filename), line_nr))).ljust(FUNCTION_COLS, '.')

	if event == "call":
		param_section = args[:PARAM_COLS]
	else:
		param_section = ""
	buffer = "%s %s\n" % (function_section, param_section)
	logfile.write(buffer)
	logfile.flush()

	return tracer
