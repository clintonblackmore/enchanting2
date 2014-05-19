class Literal:
	"""Represents a single value.
	It might be a number, a boolean, a string, or so on.
	It is not a variable, and has no name."""
	
	# I am not sure yet if this should do booleans as well or not
	# A list, on the other hand, is a separate beast
	# (it'll need to keep track of changes in time differently,
	# for example).  Also note sure about functions, etc.
	
	def __init__(self, value = None):
		self.set_value(value)
		
	def set_value(self, value):
		"""Turns the value into a number, if possible
		Otherwise, leaves it a string or None"""
		try:
			self.value = float(value)
		except:
			self.value = value
		
	def deserialize(self, elem):
		"Load from an xml element tree"
		assert(elem.tag == "l")
		self.set_value(elem.text)
	
	def serialize(self):
		"Save out as an element tree"
		literal = Element("l")
		if self.value is not None:
			literal.text = str(value)
		return literal
		
	def __eq__(self, other):
		return self.value == other.value
		
	# expose as different types
	def as_number(self):
		try:
			return float(self.value)
		except:
			return 0

	def as_string(self):
		if self.value is None:
			return ""
		# Eliminate trailing ".0" from numbers
		if isinstance(self.value, float) and (self.value == int(self.value)):
			return str(int(self.value))
		return str(self.value)
		
	# may need to add things like bool, nil, function, etc.
	