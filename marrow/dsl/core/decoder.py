# encoding: utf-8

from __future__ import unicode_literals

from codecs import register
from operator import methodcaller
from pkg_resources import iter_entry_points
from weakref import proxy

from ...package.loader import load
from ..compat import py2, str
from ..exc import TranslationError
from .context import Context


log = __import__('logging').getLogger(__name__)


class GalfiDecoder(object):
	"""A rich, buffering line transformer.
	
	Attributes:
	
	- The `_name` of the encoding, without flags or options.
	- A cached `_codec_info` `codecs.CodecInfo` instance.
	- The names of assigned `_options`.
	- The entry point `_namespace` to examine for available filters, assignable as the `ns` option.
	
	Encoding names are restricted in the allowable characters (the regular expression `[-\w.]+`) and as such follow
	a simple serializaiton mechanism:
	
	1. A galfi decoder without flags or options uses the bare decoder name, e.g. `cinje`.
	2. If flags are present, they are sorted joined together and to the name with periods, e.g. `cinje.raw`.
	3. If options are present, the keys are sorted and values are joined with hyphens, then joined as per flags, e.g.
		`cinje.raw.ns-html`.
	"""
	
	# Optional in subclasses: `_flags`, additional named options.
	__slots__ = ('_name', '_codec_info', '_options', '_namespace', '_translators')
	
	# To allow customization.
	Context = Context
	
	def __init__(self, name, *flags, **options):
		log.debug("Constructing new {0.__class__.__name__} instance: {name} *{flags} **{options}".format(
				self,
				name = name,
				flags = flags,
				options = options,
			))
		
		self._name = name
		self._assign_flags(flags)
		self._assign_options(options)
		self._codec_info = self._codec
		
		# Load the individual translators.
		# TODO: Conditional requirements...
		self._translators = [translator.load() for translator in iter_entry_points(self._namespace)]
		
		# Load translators from the parent namespace, if a child namespace was given.
		if options['ns']:
			parent = (translator.load() for translator in iter_entry_points(self._namespace.rpartition('.')[0]))
			parent = (translator for translator in parent if getattr(translator, 'inheritable', True))
			self._translators = list(parent) + self._translators
		
		self._translators.sort(key=lambda handler: handler.priority)
		
		log.debug("Prepared {0.__class__.__name__} instance for {0} with {n} translators from the {0._namespace} namespace.".format(
				self,
				n = len(self._translators)
			))
	
	@property
	def flags(self):
		return getattr(self, '_flags', set())
	
	def _assign_flags(self, flags):
		"""Global processing flags. Subclass and add `_flags` to your `__slots__` to accept flags."""
		
		flags = set(str(flag) for flag in flags)
		
		try:
			if not flags.issubset(self.FLAGS):
				unknown = flags - self.FLAGS
				plural = "" if len(unknown) == 1 else "s"
				
				raise TypeError("{name} decoder received unknown flag{plural}: {flags}".format(
						name = name,
						plural = plural,
						flags = ", ".join(sorted(unknown))
					))
			
			self._flags = flags
		
		except AttributeError:
			raise TypeError(name + " decoder does not support flags.")
	
	def _assign_options(self, options):
		options.setdefault('ns', None)
		
		for k, v in options.items():  # Named key=value pairs.
			if k[0] == '_':
				raise TypeError("May not assign options to protected attributes of a " + name + " decoder.")
			
			try:
				setattr(self, k, v)  # Assign the attribute.  Use `__slots__` to declare valid attributes.
			except AttributeError:
				raise TypeError(name + " decoder does not support the `" + k + "` option.")
		
		self._options = sorted(options)
	
	@classmethod
	def new(cls, declaration):
		"""Parse a declaration and initialize the decoder instance using extracted name, flags, and options.
		
		This allows individual encodings to more easily customize how their names are processed.
		"""
		
		flags = set()
		options = {}
		
		name, _, parts = declaration.partition('.')
		parts = parts.split('.')
		
		for part in parts:
			if '-' in part and part not in cls.FLAGS:
				k, _, v = part.partition('-')
				options[k] = v
				continue
			
			flags.add(part)
		
		return cls(name, *flags, **options)
	
	@property
	def ns(self):
		return None if self._namespace.count('.') == 2 else self._namespace.rpartition('.')[2]
	
	@ns.setter
	def ns(self, value):
		if value is None:
			self._namespace = 'marrow.dsl.' + self._name
		else:
			self._namespace = 'marrow.dsl.' + self._name + '.' + value
	
	def __str__(self):
		"""Form the canonical encoding name for this encoding, with the given flags and options."""
		
		parts = [('.' + i) for i in sorted(getattr(self, '_flags', ()))]
		
		options = ((k, getattr(self, k, None)) for k in self._options)  # Capture options.
		options = (i for i in options if i[1] is not None)  # Reject unset options.
		parts.extend(('.' + k + "-" + str(v)) for k, v in options)  # Render.
		
		return self._name + "".join(parts)
	
	if py2:
		__unicode__ = __str__
		del __str__
	
	@property
	def _codec(self):
		from codecs import Codec, CodecInfo, StreamReader, StreamWriter, IncrementalEncoder, IncrementalDecoder
		
		decoder = self
		
		class GalfiCodec(Codec):
			def encode(self, string, errors="strict"):
				raise UnicodeError("Codec incapable of encoding: " + self._name)
			
			def decode(self, string, errors="strict"):
				return decoder._decode(string, errors=errors)
		
		class GalfiStreamReader(GalfiCodec, StreamReader): pass
		class GalfiStreamWriter(GalfiCodec, StreamWriter): pass
		
		class GalfiIncrementalEncoder(IncrementalEncoder):
			def __init__(self, errors="strict"):
				raise UnicodeError("Codec incapable of encoding: " + decoder._name)
		
		class GalfiIncrementalDecoder(IncrementalDecoder):
			def __init__(self, errors="strict"):
				if errors != 'strict':
					raise UnicodeError("Unsupported value for 'errors': " + errors)
				
				super(GalfiIncrementalDecoder, self).__init__(errors)
			
			def decode(self, string, final=False):
				self.buffer += string
				
				if final:
					return decoder._decode(self.buffer, errors=self.errors)
				else:
					return ""
		
		return CodecInfo(
				name = str(self),
				encode = self._encode, decode = self._decode,
				incrementalencoder = GalfiIncrementalEncoder,
				incrementaldecoder = GalfiIncrementalDecoder,
				streamreader = GalfiStreamReader,
				streamwriter = GalfiStreamWriter,
			)
	
	def _encode(self, string, errors='strict'):
		raise UnicodeError("Codec incapable of encoding: " + self._name)
	
	def _decode(self, string, errors='strict'):
		"""An implementation of the Python unicode decoder interface.
		
		Line-ify, perform minimal preprocessing, and then coalesce the streaming decoder. Additionally, track byte
		progress to perform line/column translation and substring extraction in the event of an error.
		"""
		
		if errors != 'strict':
			raise UnicodeError("Unsupported value for 'errors': " + errors)
		
		try:
			result = self(string.decode('utf8', errors))
		
		except TranslationError as e:
			offset = 0  # TODO: Offset calculation.
			length = len(string)
			substring = b""  # TODO: Substring extraction.
			
			raise UnicodeDecodeError(str(self), substring, offset, length, str(e))
		
		except Exception as e:
			raise UnicodeDecodeError(str(self), b"", 0, len(string), str(e))
		
		return result, len(string)
	
	def __call__(self, input):
		"""Return input text transformed using plugin transformers.
		
		This prepares a context then calls `self.decode(context)` to perform the real work.
		"""
		
		context = self.Context(self, input, self._translators)
		
		stream = list(context.stream)
		
		return self.decode(stream, True), self.decode(stream, False)
	
	def decode(self, stream, r=False):
		"""Galfi decoders implement a streaming line based generation system.
		
		Certain block processors may internally buffer lines before yielding them together.
		"""
		
		return "\n".join((repr if r else str)(line) for line in stream)


def galfi(name):
	"""Look up an encoding name for processing via galfi DSL."""
	
	log.debug("Galfi asked about " + repr(name) + " encoding.")
	
	# TODO: Special case the literla "galfi" encoding to support decoder chaining.
	
	short, _, _ = name.partition('.')
	Decoder = load(short, 'marrow.dsl', default=None)
	
	if not Decoder:
		return None
	
	decoder = Decoder.new(name)
	log.debug("Instantiated galfi decoder: " + repr(decoder))
	
	return decoder._codec_info

register(galfi)
