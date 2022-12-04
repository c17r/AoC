from os import environ

__all__ = [
	'get_raw',
	'get_lines',
	'handle_result',
	'process_lines',
]

environ["AOCD_DIR"] = "./.aocd"
environ["AOCD_CONFIG_DIR"] = "./.aocd"

from aocd import get_data, submit # needs to be AFTER the environ lines so it can find the tokens

def get_raw(year, day, post=None):
	rv = get_data(year=year, day=day)
	return rv if post is None else post(rv)


def get_lines(year, day, post=None):
	return get_raw(year, day, post).splitlines()


def process_lines(year, day, parser=str, sep='\n'):
	return [parser(section) for section in get_raw(year, day).split(sep)]


def handle_result(value, year, day, part, both=True):
	print(value)
	if both:
		submit(value, year=year, day=day, part=part, reopen=False)
