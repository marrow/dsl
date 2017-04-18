# encoding: utf-8

from __future__ import unicode_literals

from collections import deque

from ..compat import py2, str
from .line import Line


class Buffer(object):
	"""An annotated iterable (and not seekable or indexable) buffer of lines.
	
	The entire buffer may have tags associated with it; these are inherited by lines within the buffer.
	
	Attributes:
	
	- `scope`: The scope level added to every line when iterated.
	- `lines`: The buffer of individual Line instances.
	- `tag`: A set of tags to associate with each line when iterated.
	- 
	"""
	
	__slots__ = ('scope', 'lines', 'tag')
	
	def __init__(self, lines, scope=0, tags=None):
		"""Construct a new buffer.
		
		You may define a base scope (added to all line scopes when iterated) and tag set. "Private tags" prefixed with
		an underscore will not be passed down to lines. Tags are effectively viral when copied from buffer to buffer.
		"""
		
		self.lines = deque((Line(l, i+1) for i, l in enumerate(lines.split("\n"))) if isinstance(lines, str) else lines)
		self.scope = scope
		self.tag = set(tags) if tags else set()
	
	@property
	def count(self):
		"""Retrieve the total number of lines stored in this buffer."""
		
		return len(self.lines)
	
	def __len__(self):
		"""Conform to Python API expectations for length retrieval."""
		
		return self.count
	
	def __repr__(self):
		"""Produce a programmers' representation giving general information about buffer state."""
		
		return '{0.__class__.__name__}({0.count}{1}{2}, scope={0.scope})'.format(
				self, ', ' if self.tag else '', ', '.join(self.tag))
	
	def __iter__(self):
		"""We conform to the Python iterator protocol, so we return ourselves here."""
		
		return self
	
	def __next__(self):
		"""Python iterator protocol to retrieve the next line."""
		
		return self.next()
	
	def __str__(self):
		"""Flatten the buffers back into a single newline-separated string."""
		
		return "\n".join(str(i) for i in self)
	
	if py2:  # Python 2 compatibility glue.
		__unicode__ = __str__
		del __str__
	
	def next(self):
		"""Retrieve and remove (pull) the first line in the next non-empty buffer or raise StopIteration."""
		
		if not self.lines:
			raise StopIteration()
		
		line = self.lines.popleft()
		return line.clone(scope=self.scope + (line.scope or 0), tags=self.tag | line.tag)
	
	def pull(self):
		"""Retrieve and remove (pull) the first line in the next non-empty buffer or return None."""
		
		if not self.lines:
			return None
		
		line = self.lines.popleft()
		return line.clone(scope=self.scope + (line.scope or 0), tags=self.tag | line.tag)
	
	def peek(self):
		"""Retrieve the next line without removing it from its buffer, or None if there are no lines available."""
		
		if not self.lines:
			return None
		
		line = self.lines[0]
		return line.clone(scope=self.scope + (line.scope or 0), tags=self.tag | line.tag)
	
	def push(self, *lines):
		"""Push one or more lines back to the head (left edge) as if they were never pulled."""
		
		self.lines.extendleft((line if isinstance(line, Line) else Line(line)) for line in reversed(lines))
	
	def append(self, *lines):
		"""Append one or more lines to the tail (right edge) of the buffer."""
		
		self.lines.extend((line if isinstance(line, Line) else Line(line)) for line in lines)
