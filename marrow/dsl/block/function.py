# encoding: utf-8

from __future__ import unicode_literals

import re

from .common import fetch_docstring
from .interface import BlockTransformer


log = __import__('logging').getLogger(__name__)


class FunctionTransformer(BlockTransformer):
	"""Proces function declarations.
	
	
	Tracks:
	
	* `name` - the name of the function
	* `buffer` - the named collection of buffers
	
	Functions are divided into:
	
	* `decorator`
	* `declaration`
	* `docstring`
	* `prefix`
	* `function`
	* `suffix`
	* `trailer`
	"""
	
	__slots__ = ('name', )
	__buffers__ = ('decorator', 'declaration', 'docstring', 'prefix', 'function', 'suffix', 'trailer')
	__buffer_default__ = 'function'
	
	priority = -900
	
	# Patterns to search for bare *, *args, or **kwargs declarations.
	STARARGS = re.compile(r'(^|,\s*)\*([^*\s,]+|\s*,|$)')
	STARSTARARGS = re.compile(r'(^|,\s*)\*\*\S+')
	
	def __init__(self, decoder):
		super(FunctionTransformer, self).__init__(decoder)
		
		self.name = None
		
		for buf in ('docstring', 'prefix', 'function', 'suffix', 'trailer'):
			self.buffer[buf].scope = 1
	
	@classmethod
	def match(cls, context, line):
		"""Match code lines using the "def" keyword."""
		
		if 'decorator' in line.tag:  # Dig a little more to identify if these are decorating a function.
			lines = list(context.only('decorator', 'comment', 'blank'))  # Extract decorators.
			line, = list(context.only('def', 'class'))  # Find the declaration.
			lines.append(line)  # Add the declaration to our list of lines.
			context.push(*lines)  # Put everything back.
		
		return 'def' in line.tag
	
	def __call__(self, context):
		buffer = self.buffer
		kind = 'closure' if 'function' in context else 'function'
		context.add(kind)
		context[kind] = self
		
		if __debug__:
			log.debug("Preparing " + kind + " context.")
		
		for line in context.only('decorator', 'comment', 'blank'):
			buffer['decorator'].append(line)
		
		declaration = self.process_declaration(context, context.only('def', 'continued'))
		buffer['declaration'].append(*declaration)
		
		fetch_docstring(context, buffer['docstring'])
		
		if __debug__:
			log.debug('{} context prepared:\n\t{}'.format(
					kind.title(),
					repr(buffer).replace('), ', ')\n\t\t')
				))
		
		self.ingress(context)
		
		for line in context.stream:
			if '_end' not in line.tag:
				buffer.append(line)
		
		self.egress(context)
		context.remove(kind)
		del context[kind]
		
		if __debug__:
			log.debug('{} complete:\n\t{}'.format(
					kind.title(),
					repr(buffer).replace('), ', ')\n\t\t')
				))
		
		# Produce the buffered results.
		for line in buffer:
			yield line
	
	def process_declaration(self, context, declaration):
		lines = list(declaration)
		logical = []
		
		for line in lines:
			line = line.line.rstrip('\\') if 'continued' in line.tag else line.line
			line.rstrip()
			logical.append(line)
			if line[-1] == ',': logical.append(' ')
		
		logical = ''.join(logical)
		
		self.name = logical.partition(' ')[2].lstrip().partition('(')[0].rstrip()
		
		for line in lines:
			yield line
	
	def ingress(self, context):
		"""Code to be executed when entering the context of a function.
		
		Always call super() first in any subclasses.
		"""
		
		pass
	
	def egress(self, context):
		"""Code to be executed when exiting the context of a function.
		
		Always call super() last in any subclasses.
		"""
		
		pass
