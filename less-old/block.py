from xml.etree.cElementTree import Element

#from ops import bind_to_function
#import ops.utilities.bind_to_function as bind_to_function

import factory
import util

class Block:
	"""This is a code block, representing an instruction to execute"""
	
	def __init__(self):
		self.function = None	# used to actually call the function
		self.function_name = ""	# the original, textual name of the function
		self.arguments = []
								
	def deserialize(self, elem):
		"Load from an xml element tree"
		assert(elem.tag == "block") # or elem.tag == "custom-block")
		self.function_name = elem.get("s")
		self.function = ops.bind_to_function(self.function_name)
			
		self.arguments.clear()
		for child in elem:
			self.arguments.append(factory.deserialize_value(child))
	
	def serialize(self):
		"Save out as an element tree"
		block = Element("block", s=self.function_name)
		for arg in self.arguments:
			block.append(arg.serialize())
		return block
		
	def evaluate(self, target):
		# evaluate each of the arguments
		args = [arg.evaluate(target) for arg in self.arguments]
		
		# now, run this function
		result = self.function(target, args)		
	
		# to do -- save args and result with timestamp
		
		return result
		