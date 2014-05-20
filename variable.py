from xml.etree.cElementTree import Element

from literal import Literal

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
			child = elem[0]
			if child.tag == "l":
				l = Literal()
				l.deserialize(child)
				self.contents = l
			# and so forth with other types
			assert(self.contents is not None)
	
	def serialize(self):
		"Save out as an element tree"
		variable = Element("variable", name=self.name)
		if self.contents is not None:
			variable.append(self.contents.serialize())
		return variable
		
	def as_number(self):
		if self.contents is not None:
			return self.contents.as_number()
		return 0
			
	def as_string(self):
		if self.contents is not None:
			return self.contents.as_string()
		return ""
	
	
			