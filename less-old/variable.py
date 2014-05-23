from xml.etree.cElementTree import Element

from literal import Literal
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
				
	def value(self):
		if self.contents is not None:
			return self.contents
		return Literal(None)
			
	def show(self, visible):
		# to do -- record if a variable is to be shown or hidden
		pass
		

	
			