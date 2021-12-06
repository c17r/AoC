from time import perf_counter_ns

__all__ = [
	'timeit',
	'inout'
]


def timeit(method):
	def timed(*args, **kw):
		ts = perf_counter_ns()
		result = method(*args, **kw)
		te = perf_counter_ns()
		duration = int(te - ts) / 1000000
		if 'log_time' in kw:
			name = kw.get('log_name', method.__name__.upper())
			kw['log_time'][name] = duration
		else:
			print(f"{method.__name__} {duration:2.2f} ms")
		return result
	return timed


def inout(show_in=False):
	def decorator(method):
		name = method.__name__
		def inner(*args, **kwargs):
			if show_in:
				print(f"({name} IN", end="")
				if len(args) > 0: 
					print(" ", end="")
					print(args, end="")
				if len(kwargs.keys()) > 0:
					print(" ", end="")
					print(kwargs, end="")
				print(")")
			else:
				print(f"({name} IN)")
			rv = method(*args, **kwargs)
			print(f"({name} OUT {rv})")
			return rv
		return inner
	return decorator
