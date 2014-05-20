from xml.etree.cElementTree import Element

import util

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
		"In order of priority, value is a boolean, number, or string"
		if isinstance(value, bool):
			self.value = value
		else:
			try:
				self.value = float(value)
			except:
				self.value = value
		
	def deserialize(self, elem):
		"Load from an xml element tree"
		assert(elem.tag == "l" or elem.tag == "bool")
		if elem.tag == "l":
			self.set_value(elem.text)
		else: # elem.tag == "bool":
			self.set_value(elem.text == "true")
	
	def serialize(self):
		"Save out as an element tree"
		if isinstance(self.value, bool):
			literal = Element("bool")
			literal.text = self.as_string()
			return literal

		literal = Element("l")
		if self.value is not None:
			if isinstance(self.value, float):
				literal.text = util.number_to_string(self.value)
			else:
				literal.text = str(self.value)
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
		if isinstance(self.value, float):
			return util.number_to_string(self.value)	# no trailing .0
		if isinstance(self.value, bool):
			return "true" if self.value else "false"	# all lowercase
		return str(self.value)
		
	def as_bool(self):
		return bool(self.value)
	
	# may need to add things like bool, nil, function, etc.
	