# encoding: utf-8

from __future__ import unicode_literals

from ..core.interface import Transformer
from ..core.lines import Lines


class BlockTransformer(Transformer):
	"""The basic definition of a block transformer.
	
	Subclass this and implement 
	"""
	
	__slots__ = ('buffer')
	__buffers__ = ()
	__buffer_tags__ = set()
	__buffer_default__ = None
	
	def __init__(self, decoder):
		super(BlockTransformer, self).__init__(decoder)
		
		self.buffer = Lines(*self.__buffers__, default=self.__buffer_default__, tags=self.__buffer_tags__)
	
	@classmethod
	def match(cls, context, line):
		raise NotImplementedError()
	
	def __call__(self, context):
		raise NotImplementedError()
	
	def __getitem__(self, name):
		return self.buffer[name]
	
	def __getattr__(self, name):
		if name not in self.buffer:
			raise AttributeError()
		
		return self.buffer[name]
