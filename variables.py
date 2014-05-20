from xml.etree.cElementTree import Element
from collections import OrderedDict

from variable import Variable

class Variables:
	"""This is a collection of 'Variable' objects, as used by the project, stage, and sprites"""
	
	def __init__(self):
		# ordered dict so we can serialize in the order we deserialized
		# (possibly doesn't really matter, but it helps with the unit tests)
		self.variables = OrderedDict()	
		
	def get_variable(self, name):
		if name in self.variables:
			return self.variables[name]
		return None
		
	def add(self, v):
		self.variables[v.name] = v
		
	def deserialize(self, elem):
		"Loads this class from an element tree representation"
		assert(elem.tag == "variables")
		
		# Read in all the variables
		self.variables.clear()
		for child_node in elem:
			v = Variable()
			v.deserialize(child_node)
			self.add(v)
		
	def serialize(self):
		"Return an elementtree representing this object"
		variables = Element("variables")
		for child in self.variables.values():
			variables.append(child.serialize())
		return variables

	
	
