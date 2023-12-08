from os import environ

__all__ = [
	'get_raw',
	'get_lines',
	'handle_result',
	'process_lines',
	'example_raw',
	'example_lines',
	'example_process',
]

environ["AOCD_DIR"] = "./.aocd"
environ["AOCD_CONFIG_DIR"] = "./.aocd"

from aocd import get_data, submit # needs to be AFTER the environ lines so it can find the tokens
from aocd.models import Puzzle

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

def get_example(year, day, part="a"):
	idx = 0 if part == "a" else -1
	puzzle = Puzzle(year, day)
	return puzzle.examples[idx].input_data

def example_raw(year, day, part="a", post=None):
	rv = get_example(year, day, part)
	return rv if post is None else post(rv)

def example_lines(year, day, part="a", post=None):
	return example_raw(year, day, part, post).splitlines()

def example_process(year, day, part="a", parser=str, sep='\n'):
	return [parser(section) for section in example_raw(year, day, part).split(sep)]
