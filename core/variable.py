from xml.etree.cElementTree import Element

import factory

class Variable:
	"""Represents a value that changes over time.  
	Contains something like a Literal, Bool, or List"""
	
	def __init__(self, contents = None, name = "No name"):
		self.contents = contents
		self.name = name
		
	def deserialize(self, elem):
		"Load from an xml element tree"
		assert(elem.tag == "variable")
		self.name = elem.get("name")

		# We should have one child
		self.contents = None
		if len(elem) > 0:
			self.contents = factory.deserialize_value(elem[0])
			assert(self.contents is not None)
	
	def serialize(self):
		"Save out as an element tree"
		variable = Element("variable", name=self.name)
		if self.contents is not None:
			variable.append(self.contents.serialize())
		return variable
		
	def set(self, value):
		"Sets a variable.  Pass in a Literal or other object as a value"
		self.contents = value
		# to do -- record if there has been a change
		
	def increment(self, incr):
		self.set(self.as_number() + incr.as_number())
		
	def as_number(self):
		if self.contents is not None:
			return self.contents.as_number()
		return 0
			
	def as_string(self):
		if self.contents is not None:
			return self.contents.as_string()
		return ""
	
	
			