# encoding: utf-8

from __future__ import unicode_literals

from collections import deque

from .buffer import Buffer
from .compat import py2, str
from .line import Line


log = __import__('logging').getLogger(__name__)


def _pub(a):
	return {i for i in a if i[0] != '_'}


class Lines(object):
	"""An iterable set of named, indexed buffers containing lines, able to push lines back during iteration.
	
	Access as a dictionary using string keys to access named buffers.
	
	Attributes:
	
	- `buffers`: A mapping of buffer name to buffer.
	- `lines`: A deque of the buffers in order.
	- `active`: A reference to the last manipulated buffer.
	"""
	
	__slots__ = ('buffers', 'lines', 'active')
	
	def __init__(self, buffers, *args, **kw):
		"""Construct a new set of buffers for the given input, or an empty buffer."""
		
		tags = kw.pop('tags', None)
		self.buffers = {}  # Named references to buffers.
		self.lines = deque()  # Indexed references to buffers.
		
		if isinstance(buffers, str) and args:
			buffers = [(i, Buffer(())) for i in [buffers] + list(args)]
		
		elif isinstance(buffers, str):
			buffers = [('default', Buffer(buffers))]
		
		elif isinstance(buffers, Lines):
			self.buffers = buffers.buffers.copy()
			self.lines.extend(buffers.lines)
			buffers = ()
		
		for name, buffer in buffers:
			if isinstance(buffer, str):
				buffer = Buffer(buffer)
			
			self.buffers[name] = buffer
			self.lines.append(buffer)
		
		if tags:
			for buffer in self.lines:
				buffer.tag |= tags
		
		if 'default' in kw and kw['default']:
			self.active = self.buffers[kw['default']]
		else:
			self.active = self.lines[0] if self.lines else None
		
		super(Lines, self).__init__()
	
	def __len__(self):
		"""Conform to Python API expectations for length retrieval."""
		
		return self.count
	
	def __repr__(self):
		"""Produce a programmers' representation giving general information about buffer state."""
		
		rev = {v: k for k, v in self.buffers.items()}
		buffers = ', '.join((rev[buf] + '=' + repr(buf)) for buf in self.lines)
		if buffers: buffers = ", " + buffers
		
		return '{0.__class__.__name__}({0.count}{1}, active={2})'.format(
				self, buffers, 'None' if self.active is None else rev[self.active])
	
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
	
	def __contains__(self, name):
		"""Does this group of lines contain the named buffer?"""
		
		return name in self.buffers
	
	def __getitem__(self, name):
		"""Allow retrieval of named buffers through array subscript access."""
		
		return self.buffers[name]
	
	def __setitem__(self, name, value):
		"""Allow assignment of named buffers through array subscript assignment."""
		
		if not isinstance(value, Buffer):
			value = Buffer(value)
		
		self.buffers[name] = value
		if value not in self.lines:
			self.lines.append(value)
	
	def __delitem__(self, name):
		"""Allow removal of named buffers through array subscript deletion."""
		
		if name not in self.buffers:
			raise KeyError()
		
		value = self[name]
		del self.buffers[name]
		
		try:
			self.lines.remove(value)
		except ValueError:
			pass
	
	@property
	def count(self):
		"""Retrieve the total number of lines stored in all buffers."""
		
		return sum(len(i) for i in self.lines)
	
	def next(self):
		"""Retrieve and remove (pull) the first line in the next non-empty buffer or raise StopIteration."""
		
		for lines in self.lines:
			if lines: break
		else:
			raise StopIteration()
		
		self.active = lines
		
		return lines.next()
	
	def pull(self):
		"""Retrieve and remove (pull) the first line in the next non-empty buffer or return None."""
		
		for lines in self.lines:
			if lines: break
		else:
			return None
		
		self.active = lines
		
		return lines.pull()
	
	def peek(self):
		"""Retrieve the next line without removing it from its buffer, or None if there are no lines available."""
		
		for lines in self.lines:
			if lines: break
		else:
			return None
		
		self.active = lines
		
		return lines.peek()
	
	def push(self, *lines):
		self.active.push(*lines)
	
	def append(self, *lines):
		self.active.append(*lines)
