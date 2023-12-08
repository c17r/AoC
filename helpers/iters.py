import re

from collections.abc import Sequence
from collections import deque
from itertools import zip_longest, combinations, islice, chain

from .functional import mapt


cat = ''.join
first = lambda iterable: nth(iterable, 0)
map_ints = lambda ints: list(map(int, list(ints)))
get_ints = lambda line: map_ints(re.findall(r'-?\d+', line))        
transpose = lambda matrix: zip(*matrix)


def flatten(iterable):
	return list(chain(*[ele if isinstance(ele, list) 
		else [ele] for ele in iterable]))

def add(A, B): 
	"Element-wise addition of two n-dimensional vectors."
	return mapt(sum, zip(A, B))


def take(n, iterable, default=None):
	"Return first n items of the iterable as a list"
	return list(islice(iterable, n, default))


def nth(iterable, n, default=None):
	"Returns the nth item or a default value"
	return next(islice(iterable, n, None), default)


def grouper(iterable, n, fillvalue=None):
	"""Collect data into fixed-length chunks:
	grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"""
	args = [iter(iterable)] * n
	return zip_longest(*args, fillvalue=fillvalue)


def splitter(iterable, split_func, post_func=None):
	"""Splits iterable into multiple iterables, based on a split function"""
	rv = []
	for item in iterable:
		if split_func(item):
			yield rv if post_func is None else post_func(rv)
			rv = []
			continue
		rv.append(item)


def overlapping(iterable, n):
	"""Generate all (overlapping) n-element subsequences of iterable.
	overlapping('ABCDEFG', 3) --> ABC BCD CDE DEF EFG"""
	if isinstance(iterable, Sequence):
		yield from (iterable[i:i+n] for i in range(len(iterable) + 1 - n))
	else:
		result = deque(maxlen=n)
		for x in iterable:
			result.append(x)
			if len(result) == n:
				yield tuple(result)


def pairwise(iterable):
	"s -> (s0,s1), (s1,s2), (s2, s3), ..."
	return overlapping(iterable, 2)


def sequence(iterable, type=tuple):
	"Coerce iterable to sequence: leave alone if already a sequence, else make it `type`."
	return iterable if isinstance(iterable, Sequence) else type(iterable)


def join(iterable, sep=''):
	"Join the items in iterable, converting each to a string first."
	return sep.join(map(str, iterable))


def powerset(iterable):
	"Yield all subsets of items."
	items = list(iterable)
	for r in range(len(items)+1):
		for c in combinations(items, r):
			yield c
