import pyflowtrace
import sys

def fn_a(): fn_b(1, 2, "hello")

def fn_b(a, b, c): fn_c(a, b, c, d=None, e=None)

def fn_c(a, b, c, d=None, e=None, f=None):
	pass

if __name__ == "__main__":
	sys.setprofile(pyflowtrace.tracer)
	fn_a()
