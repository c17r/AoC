from time import perf_counter
__all__ = [
	'timeit'
]

def timeit(method):
	def timed(*args, **kw):
		ts = perf_counter()
		result = method(*args, **kw)
		te = perf_counter()
		if 'log_time' in kw:
			name = kw.get('log_name', method.__name__.upper())
			kw['log_time'][name] = int((te - ts) * 1000)
		else:
			print('%r  %2.2f ms' % (method.__name__, (te - ts) * 1000))
		return result
	return timed
