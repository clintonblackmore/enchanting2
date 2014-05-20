from xml.etree.cElementTree import Element

import factory
import util

class Block:
	"""This is a code block, representing an instruction to execute"""
	
	def __init__(self, target):
		self.target = target	# What entity does this block act on?
		self.function = None	# used to actually call the function
		self.raw_selector = ""	# the original, textual name of the function
		self.arguments = []
				
	def find_function(self, selector):
		self.raw_selector = selector
		try:
			self.function = getattr(self.target, selector)
		except AttributeError:
			self.function = None
				
	def deserialize(self, elem):
		"Load from an xml element tree"
		assert(elem.tag == "block") # or elem.tag == "custom-block")
		if elem.tag == "block":
			self.set_value(elem.text)
		self.find_function(elem.get("s"))	
			
		self.arguments.clear()
		for child in elem:
			self.arguments.append(factory.deserialize_value(child))
	
	def serialize(self):
		"Save out as an element tree"
		block = Element("block", s=self.raw_selector)
		for arg in self.arguments:
			block.append(arg.serialize())
		return block
		
	def evaluate(self):
		pass
		# to do
		
		