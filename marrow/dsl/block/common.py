# encoding: utf-8

from __future__ import unicode_literals

from ..exc import TranslationError


def fetch_docstring(context, buffer):
	"""Retrieve a docstring from the stream, placing the result into a specific buffer.
	
	This explicitly does not handle the pathalogical case of placing a comment at the end of the same line terminating
	the docstring itself. Nor are string prefixes such as `r` or `u` handled. Please don't do these things to your
	docstrings, they're silly.
	
	For use in block transformers handling module, class, or function scopes.
	"""
	
	starting = None  # Line number the docstring begins on.
	quotes = None  # The quotes detected as used to define the string literal.
	
	for line in context.only('code', 'blank'):  # Identify the docstring.
		text = line.stripped
		
		if not quotes and text[0] not in ('"', "'"):
			# Docstrings must be the first string literal within the scope.
			context.push(line)
			break
		
		if not quotes:  # Identify how the string literal is quoted.
			quotes = (3 if text[:3].count(text[0]) == 3 else 1) * text[0]  # " " -> single quoted string
			starting = line.number
		
		# Append and annotate the line as being a docstring.
		buffer.append(line.clone(tags=line.tag | {'docstring'}))
		
		if text.endswith(quotes):
			break  # Stop if we've reached the end of the docstring.
	
	else:  # We've run out of matching source material.
		if quotes:
			raise TranslationError(
					"Unterminated docstring literal using {!r} starting on line {}.".format(quotes, starting),
					quotes,
					starting
				)
	
	for line in context.only('blank'):
		buffer.append(line)  # Blank lines trailing after the docstring are considered part of the docstring block.
