from os import environ
__all__ = [
	'get_raw',
	'get_lines',
	'handle_result',
]

environ["AOCD_DIR"] = "./.aocd"

from aocd import get_data, submit

def get_raw(year, day, post=None):
	rv = get_data(year=year, day=day)
	if post is not None:
		rv = post(rv)
	return rv

def get_lines(year, day, post=None):
	return get_raw(year, day, post).splitlines()

def handle_result(value, year, day, part, both=True):
	print(value)
	if both:
		submit(value, year=year, day=day, part=part)
