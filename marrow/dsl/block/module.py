# encoding: utf-8

from __future__ import unicode_literals

from collections import defaultdict as ddict

from ..compat import py2, str
from ..core import Line
from .common import fetch_docstring
from .interface import BlockTransformer
from .util import redelta_encode


log = __import__('logging').getLogger(__name__)


class ModuleTransformer(BlockTransformer):
	"""Module transformer.
	
	This is the initial scope, and the highest priority to ensure its processing of the preamble happens first.
	"""
	
	__slots__ = ('imports')
	
	__buffers__ = ('comment', 'docstring', '_imports', 'prefix', 'module', 'suffix')
	__buffer_tags__ = {'module'}
	__buffer_default__ = 'module'
	
	priority = -1000
	
	FUTURES = {'absolute_import', 'division', 'print_function', 'unicode_literals'}
	
	def __init__(self, decoder):
		super(ModuleTransformer, self).__init__(decoder)
		
		# Prepare our module-scoped buffers.
		self.module.tag.discard('module')
		self._imports = ddict(set)
	
	@classmethod
	def match(cls, context, line):
		return 'init' not in context
	
	def __call__(self, context):
		if __debug__:
			log.debug("Preparing module context.")
		
		buffer = self.buffer
		context.add('init')
		context.module = self  # Give other transformers access to our (global) scope.
		
		if __debug__:
			log.debug("Module context prepared:\n\t" + repr(buffer).replace('), ', ')\n\t\t'))
		
		for line in context.only('comment', 'blank'):  # Pull out any module comment prefix, e.g. encoding, shbang, etc.
			buffer.comment.append(line)
		
		fetch_docstring(context, buffer['docstring'])
		
		for line in context.only('import', 'blank'):
			buffer.imports.append(line)
		
		self.ingress(context)  # Easy subclass hook to perform any additional work just prior to entering the stream.
		
		for line in context.stream:
			if '_end' not in line.tag:
				buffer.append(line)
		
		self.egress(context)  # Easy subclass hook to perform any additional work prior to line mapping.
		
		if __debug__:
			log.debug("Module complete:\n\t" + repr(buffer).replace('), ', ')\n\t\t'))
		
		# Finally, emit the buffered result.
		
		if 'nomap' in context:
			for line in buffer:
				yield line
			return
		
		for line in self.emit_with_mapping(buffer):
			yield line
	
	def emit_with_mapping(self, buffer):
		needs_mapping = None if 'nomap' in buffer else False
		mapping = []
		
		for line in buffer:
			if needs_mapping is False:
				if not needs_mapping and (not line.number or (mapping and mapping[-1] != line.number - 1)):
					needs_mapping = True
			
			if needs_mapping is not None:
				mapping.append(line.number if line.number else -1)
			
			yield line
		
		if needs_mapping:  # Map line numbers to aid in debugging, but only if lines were added or re-ordered.
			yield Line("")
			yield Line("# Line number mappings for translating errors back to the source file.")
			yield Line('__gzmapping__ = b"' + redelta_encode(mapping).replace('"', '\"') + '"')
			
			# Uncompressed version for readability in development.
			if __debug__:
				yield Line('__mapping__ = [' + ','.join(str(i) for i in mapping) + ']')
	
	def ingress(self, context):
		"""Code to be executed when entering the context of the module.
		
		Always call super() first in any subclasses.
		"""
		
		pass
	
	def egress(self, context):
		"""Code to be executed when exiting the context of the module.
		
		Always call super() last in any subclasses.
		"""
		
		imports = self._imports
		
		if py2:  # Add __future__ imports on Python 2 runtimes.
			imports['__future__'].update(self.FUTURES)
		
		if imports:
			futures = imports.pop('__future__', ())  # Extract these from general processing.
			
			# TODO: Split stdlib from third-party. Ref: sys.builtin_module_names
			# TODO: Make module ordering style configurable.
			
			for package, objs in sorted(imports.items()):
				if not objs: continue  # Skip queried, but empty packages.
				self.imports.append('from {} import {}'.format(package, ', '.join(sorted(objs))))
			
			self.imports.append('', '')
			
			if futures:
				self.imports.push('from __future__ import ' + ', '.join(sorted(imports.pop('__future__'))), '')
