# encoding: utf-8

from __future__ import unicode_literals

from ..compat import py2, str
from .buffer import Buffer


log = __import__('logging').getLogger(__name__)


class Context(object):
	"""The processing context for translating DSL source into Python source.
	
	"""
	
	__slots__ = ('decoder', 'input', 'flag', 'scope', 'buffers', 'scopes', 'classifiers', 'transformers')
	
	def __init__(self, decoder, input, translators):
		log.debug("Constructing new context.")
		
		self.decoder = decoder
		self.input = Buffer(input)
		self.flag = set(decoder.flags)
		self.classifiers = []
		self.transformers = []
		self.buffers = []
		self.scopes = {}
		
		for translator in translators:
			if hasattr(translator, 'classify'):
				self.classifiers.append(translator(decoder).classify)
			
			if hasattr(translator, 'match'):
				self.transformers.append(translator)
		
		log.debug(
				"Context prepared with {} classifiers, {} transformers: {!r}".format(
				len(self.classifiers),
				len(self.transformers),
				self.input,
			))
	
	def __repr__(self):
		return "Context({!r}, {})".format(self.input, self.flag)
	
	def __contains__(self, value):
		return value in self.flag
	
	def __getitem__(self, scope):
		return self.scopes[scope]
	
	def __setitem__(self, scope, value):
		self.scopes[scope] = value
	
	def __delitem__(self, scope):
		del self.scopes[scope]
	
	@property
	def buffer(self):
		return self.buffers[0] if self.buffers else None
	
	def classify(self, line):
		if 'classified' not in line.tag:
			line.tag.add('classified')
			for classify in self.classifiers:
				classify(self, line)
	
	def __iter__(self):
		for line in self.input:
			self.classify(line)
			yield line
	
	def add(self, value):
		self.flag.add(value)
	
	def remove(self, value):
		if value in self.flag:
			self.flag.remove(value)
	
	def toggle(self, value):
		if value in self.flag:
			self.flag.remove(value)
		else:
			self.flag.add(value)
	
	def pull(self):
		return self.input.pull()
	
	def peek(self):
		line = self.input.peek()
		self.classify(line)
		return line
	
	def push(self, line):
		self.classify(line)
		self.input.push(line)
	
	def transformer_for(self, line):
		"""Identify the correct translator for a given line of input."""
		
		for Transformer in self.transformers:
			if Transformer.match(self, line):
				return Transformer(self.decoder)
	
	def only(self, *tags):
		for line in self:
			if not line.tag & set(tags):
				self.push(line)
				return
			
			yield line
	
	@property
	def stream(self):
		"""The workhorse of cinje: transform input lines and emit output lines.
		
		After constructing an instance with a set of input lines iterate this property to generate the template.
		"""
		log.debug("Entering the stream.")
		
		for line in self:
			log.debug("Processing " + repr(line) + " with " + repr(self))
			handler = self.transformer_for(line)
			
			if '_end' in line.tag:  # Exit the current child scope.
				yield line
				return
			
			if handler is None:
				log.debug("No handler for line.")
				yield line  # Nothing to transform, pass through.
				continue
			
			self.input.push(line)  # Put it back so it can be consumed by the handler.
			
			for line in handler(self):  # This re-indents the code to match, if missing explicit scope.
				if line.scope is None:
					line = line.clone(scope=self.input.scope)
				
				yield line
