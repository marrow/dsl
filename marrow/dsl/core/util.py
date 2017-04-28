# encoding: utf-8

from __future__ import unicode_literals

from base64 import b64encode
from zlib import compress


def redelta_encode(numbers):
	"""Encode a series of line numbers as the difference from line to line (deltas) to reduce entropy.
	
	The delta is stored as a single signed byte per line, meaning no two consecutive lines may vary by more than +/-
	127 lines within the original source material. The resulting bytestring is then zlib compressed and b64 encoded.
	
	Lines without line numbers (none or unexpected zeros) will inherit the last known line number after decoding.
	"""
	
	def inner():
		lines = iter(numbers)
		prev = next(lines)
		
		for line in lines:
			delta = (line or prev) - prev  # Handle the "no line number given" case.
			if delta < 0: delta = -1 * delta + 127  # Store "signed" values.
			prev = (line or prev)  # Track our line number, or the last known good one.
			yield delta  # Store the delta.
	
	return b64encode(compress(bytes(bytearray(inner())))).decode('latin1')


def redelta_decode(source):
	"""Decode a series of line numbers encoded as the difference from line to line.
	
	The literal reverse of `redelta_encode`.
	"""
	
	pass


def chunk(line, mapping={None: 'text', '${': 'escape', '#{': 'bless', '&{': 'args', '%{': 'format', '@{': 'json'}):
	"""Chunkify and "tag" a block of text into plain text and code sections.
	
	The first delimeter is blank to represent text sections, and keep the indexes aligned with the tags.
	
	Values are yielded in the form (tag, text).
	"""
	
	skipping = 0  # How many closing parenthesis will we need to skip?
	start = None  # Starting position of current match.
	last = 0
	
	i = 0
	
	text = line.line
	
	while i < len(text):
		if start is not None:
			if text[i] == '{':
				skipping += 1
			
			elif text[i] == '}':
				if skipping:
					skipping -= 1
				else:
					yield line.clone(kind=mapping[text[start-2:start]], line=text[start:i])
					start = None
					last = i = i + 1
					continue
		
		elif text[i:i+2] in mapping:
			if last is not None and last != i:
				yield line.clone(kind=mapping[None], line=text[last:i])
				last = None
			
			start = i = i + 2
			continue
		
		i += 1
	
	if last < len(text):
		yield line.clone(kind=mapping[None], line=text[last:])
