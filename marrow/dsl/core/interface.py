# encoding: utf-8

from __future__ import unicode_literals

from .lines import Lines


class Classifier(object):
	__slots__ = ()
	
	priority = 0
	
	def __init__(self, decoder):
		pass
	
	def classify(self, context, line):
		raise NotImplementedError()


class Transformer(object):
	__slots__ = ()
	
	priority = 0
	
	def __init__(self, decoder):
		pass
