# encoding: utf-8

from __future__ import unicode_literals

from .compat import py2, str


class Line(object):
	"""A rich description for a line of input or output, allowing for annotation.
	
	Attributes:
	
	- `line`: The string value of the line.
	- `stripped`: The whitespace stripped version of the line.
	- `number`: The originating line number.
	- `scope`: The scope (generally indentation level) of the line.
	- `tag`: An optional set of tags to associate with the line.
	"""
	
	__slots__ = ('line', 'stripped', 'number', 'scope', 'tag')
	
	def __init__(self, line, number=None, scope=None, tags=None):
		self.line = line
		line = self.stripped = line.strip()
		
		self.number = number
		self.scope = scope
		self.tag = set(tags) if tags else set()
		
		if line.endswith('\\') and not line.endswith('\\\\'):
			self.tag.add('continued')
		
		super(Line, self).__init__()
	
	def __repr__(self):
		return '{0.__class__.__name__}({0.number}:{0.scope}, {0.tag}, "{0.stripped}")'.format(self)
	
	def __str__(self):
		if self.scope is None:
			return self.line
		
		return '\t' * self.scope + self.stripped
	
	if py2:
		__unicode__ = __str__
		del __str__
	
	def clone(self, **kw):
		"""Return a new Line instance as a mutatable shallow copy.
		
		This will not preserve "private" (underscore-prefixed) tags.
		"""
		
		return self.__class__(
				line = kw.get('line', self.line),
				number = kw.get('number', self.number),
				scope = kw.get('scope', self.scope),
				tags = kw['tags'] if 'tags' in kw else set(i for i in self.tag if i[0] != '_'),
			)
